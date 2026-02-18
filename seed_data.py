from app import app, db, Patient, AuditLog
from risk_engine import calculate_risk
import json

def seed_database():
    """
    Populates the database with varied sample patient data for testing and demonstration.
    """
    with app.app_context():
        # Option to clear existing data? Maybe not, just append.
        print("Seeding database with sample patients...")

        samples = [
            {
                "name": "John Doe",
                "age": 35,
                "gender": "Male",
                "heart_rate": 72,
                "systolic_bp": 120,
                "diastolic_bp": 80,
                "spo2": 98,
                "temperature": 37.0,
                "respiratory_rate": 16,
                "history": [],
                "lab_issues": [],
                "notes": "Healthy individual for baseline comparison."
            },
            {
                "name": "Sarah Smith",
                "age": 68,  # Age 60-75 (+1)
                "gender": "Female",
                "heart_rate": 105, # HR 100-120 (+1)
                "systolic_bp": 130,
                "diastolic_bp": 85,
                "spo2": 96,
                "temperature": 38.2, # Temp 38-39 (+1)
                "respiratory_rate": 18,
                "history": ["Diabetes"], # History (+1)
                "lab_issues": [],
                "notes": "Elderly patient with fever and diabetes."
            },
            {
                "name": "Robert Brown",
                "age": 82, # Age >75 (+2)
                "gender": "Male",
                "heart_rate": 130, # HR >120 (+2)
                "systolic_bp": 85, # SBP <90 (+2)
                "diastolic_bp": 50,
                "spo2": 88, # SpO2 <90 (+2)
                "temperature": 36.5,
                "respiratory_rate": 28, # Resp >24 (+1)
                "history": ["Hypertension", "COPD"], # (+2)
                "lab_issues": ["Elevated WBC"], # (+1)
                "notes": "High risk critical patient."
            },
            {
                "name": "Emily White",
                "age": 45,
                "gender": "Female",
                "heart_rate": 155, # Critical HR > 140
                "systolic_bp": 110,
                "diastolic_bp": 70,
                "spo2": 95,
                "temperature": 37.0,
                "respiratory_rate": 20,
                "history": [],
                "lab_issues": [],
                "notes": "Critical Tachycardia escalation."
            }
        ]

        for data in samples:
            # Calculate Risk
            risk_input = {
                'age': data['age'],
                'heart_rate': data['heart_rate'],
                'systolic_bp': data['systolic_bp'],
                'spo2': data['spo2'],
                'temperature': data['temperature'],
                'respiratory_rate': data['respiratory_rate'],
                'history': data['history'],
                'er_visits': 0,
                'lab_issues': data['lab_issues']
            }
            risk_res = calculate_risk(risk_input)

            patient = Patient(
                name=data['name'],
                age=data['age'],
                gender=data['gender'],
                heart_rate=data['heart_rate'],
                systolic_bp=data['systolic_bp'],
                diastolic_bp=data['diastolic_bp'],
                spo2=data['spo2'],
                temperature=data['temperature'],
                respiratory_rate=data['respiratory_rate'],
                er_visits=0,
                history=json.dumps(data['history']),
                lab_issues=json.dumps(data['lab_issues']),
                notes=data['notes'],
                risk_score=risk_res['score'],
                risk_label=risk_res['label'],
                risk_notes=json.dumps(risk_res['notes'])
            )
            db.session.add(patient)
            db.session.flush() # Generate ID

            # Create Initial Audit Log
            log = AuditLog(
                patient_id=patient.id,
                field_changed="Creation",
                old_value="N/A",
                new_value="Patient Created",
                risk_change=f"Started as {risk_res['label']}"
            )
            db.session.add(log)
        
        db.session.commit()
        print(f"Successfully added {len(samples)} sample patients.")

if __name__ == "__main__":
    seed_database()
