from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Patient, AuditLog
from risk_engine import calculate_risk
from service_pdf import extract_data_from_pdf
import os
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///risk_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'amrita_health_secret' # Needed for flash messages

# Ensure upload directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db.init_app(app)

# Helper to Initialize DB
with app.app_context():
    db.create_all()

from datetime import datetime, timedelta

@app.route('/')
def dashboard():
    patients = Patient.query.all()
    
    # 1. Recent Admissions (Last 5)
    recent_patients = Patient.query.order_by(Patient.admission_date.desc()).limit(5).all()

    # 2. Risk Distribution (Donut Chart)
    risk_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
    for p in patients:
        if p.risk_label in risk_counts:
            risk_counts[p.risk_label] += 1
            
    # 3. 7-Day Risk Trend (Line Chart) - Count of High Risk patients admitted per day
    today = datetime.utcnow().date()
    dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
    trend_data = []
    
    for date_str in dates:
        count = 0
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        # Inefficient loop for small dataset is fine
        for p in patients:
            if p.admission_date.date() == target_date and p.risk_label == 'HIGH':
                count += 1
        trend_data.append(count)

    return render_template('dashboard.html', 
                           patients=patients, 
                           recent_patients=recent_patients,
                           risk_counts=risk_counts,
                           trend_dates=dates,
                           trend_data=trend_data)

@app.route('/patients')
def patient_list():
    patients = Patient.query.order_by(Patient.admission_date.desc()).all()
    return render_template('patient_list.html', patients=patients)

@app.route('/add', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        # 1. Extract Data
        data = {
            'age': int(request.form['age']),
            'heart_rate': int(request.form['heart_rate']),
            'systolic_bp': int(request.form['systolic_bp']),
            'diastolic_bp': int(request.form['diastolic_bp']),
            'spo2': int(request.form['spo2']),
            'temperature': float(request.form['temperature']),
            'respiratory_rate': int(request.form['respiratory_rate']),
            'er_visits': int(request.form.get('er_visits', 0)),
            # Handling History List from checkbox or comma-separated string
            'history': [item.strip() for sublist in [x.split(',') for x in request.form.getlist('history')] for item in sublist if item.strip()],
            'lab_issues': [item.strip() for sublist in [x.split(',') for x in request.form.getlist('lab_issues')] for item in sublist if item.strip()]
        }

        # 2. Calculate Initial Risk (Automatic)
        risk_result = calculate_risk(data)

        # 3. Create Patient Record
        new_patient = Patient(
            name=request.form['name'],
            age=data['age'],
            gender=request.form['gender'],
            heart_rate=data['heart_rate'],
            systolic_bp=data['systolic_bp'],
            diastolic_bp=data['diastolic_bp'],
            spo2=data['spo2'],
            temperature=data['temperature'],
            respiratory_rate=data['respiratory_rate'],
            er_visits=data['er_visits'],
            history=json.dumps(data['history']),
            lab_issues=json.dumps(data['lab_issues']),
            # System Assigned Risk
            risk_score=risk_result['score'],
            risk_label=risk_result['label'],
            risk_notes=json.dumps(risk_result['notes'])
        )

        db.session.add(new_patient)
        db.session.commit()
        
        # Log Creation
        log = AuditLog(
            patient_id=new_patient.id,
            field_changed="Creation",
            old_value="N/A",
            new_value="Patient Created",
            risk_change=f"Started as {risk_result['label']}"
        )
        db.session.add(log)
        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template('add_patient.html')

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return json.dumps({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return json.dumps({'error': 'No selected file'}), 400
        
    if file:
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            data = extract_data_from_pdf(filepath)
            # clean up
            os.remove(filepath)
            return json.dumps(data)
        except Exception as e:
            return json.dumps({'error': str(e)}), 500

@app.route('/update/<int:id>', methods=['POST'])
def update_patient(id):
    patient = Patient.query.get_or_404(id)
    
    # 1. Capture Old State for Audit
    old_risk = patient.risk_label
    changes_made = []

    # Helper function to check change and log it
    def check_change(field_name, new_val, is_json=False):
        old_val = getattr(patient, field_name)
        
        # Normalize for comparison
        if is_json:
            old_comp = json.loads(old_val) if old_val else []
            new_comp = new_val
        else:
            old_comp = old_val
            new_comp = new_val

        if old_comp != new_comp:
            changes_made.append({
                'field': field_name,
                'old': str(old_comp),
                'new': str(new_comp)
            })
            # Update the object
            if is_json:
                setattr(patient, field_name, json.dumps(new_val))
            else:
                setattr(patient, field_name, new_val)

    # Check Vitals fields
    check_change('heart_rate', int(request.form['heart_rate']))
    check_change('systolic_bp', int(request.form['systolic_bp']))
    check_change('diastolic_bp', int(request.form['diastolic_bp']))
    check_change('spo2', int(request.form['spo2']))
    check_change('temperature', float(request.form['temperature']))
    check_change('respiratory_rate', int(request.form['respiratory_rate']))
    check_change('er_visits', int(request.form['er_visits']))
    # ... add other fields as needed

    # 2. Recalculate Risk (Automatic) [cite: 96]
    # We use the updated patient object to generate new data dict
    current_data = patient.to_dict()
    new_risk_result = calculate_risk(current_data)
    
    patient.risk_score = new_risk_result['score']
    patient.risk_label = new_risk_result['label']
    patient.risk_notes = json.dumps(new_risk_result['notes'])

    # 3. Save to DB and Create Audit Logs 
    risk_msg = "No Change"
    if old_risk != new_risk_result['label']:
        risk_msg = f"{old_risk} -> {new_risk_result['label']}"

    for change in changes_made:
        log = AuditLog(
            patient_id=patient.id,
            field_changed=change['field'],
            old_value=change['old'],
            new_value=change['new'],
            risk_change=risk_msg
        )
        db.session.add(log)
    
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/patient/<int:id>')
def patient_details(id):
    patient = Patient.query.get_or_404(id)
    # Sort logs by newest first so the latest changes appear at the top
    logs = sorted(patient.logs, key=lambda x: x.timestamp, reverse=True)
    
    field_labels = {
        'er_visits': 'ER Visits',
        'respiratory_rate': 'Respiratory Rate',
        'heart_rate': 'Heart Rate',
        'systolic_bp': 'Systolic BP',
        'diastolic_bp': 'Diastolic BP',
        'spo2': 'SpO2',
        'temperature': 'Temperature'
    }
    
    return render_template('patient_details.html', patient=patient, logs=logs, field_labels=field_labels)
    
if __name__ == '__main__':
    app.run(debug=True)