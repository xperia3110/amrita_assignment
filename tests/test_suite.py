import unittest
import json
import os
import shutil
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ['DATABASE_URI'] = 'sqlite:///:memory:'

from app import app, db, Patient
from risk_engine import calculate_risk
from service_pdf import extract_data_from_pdf
from reportlab.pdfgen import canvas

class TestRiskEngine(unittest.TestCase):
    def test_low_risk_young_healthy(self):
        data = {
            'age': 30, 'heart_rate': 70, 'systolic_bp': 120, 'spo2': 98,
            'temperature': 37.0, 'respiratory_rate': 16, 
            'history': [], 'er_visits': 0, 'lab_issues': []
        }
        result = calculate_risk(data)
        self.assertEqual(result['label'], 'LOW')
        self.assertEqual(result['score'], 0)

    def test_medium_risk_age_and_vitals(self):
        # Age 65 (+1), HR 105 (+1), Temp 38.5 (+1) = Score 3 -> MEDIUM
        data = {
            'age': 65, 'heart_rate': 105, 'systolic_bp': 120, 'spo2': 98,
            'temperature': 38.5, 'respiratory_rate': 16,
            'history': [], 'er_visits': 0, 'lab_issues': []
        }
        result = calculate_risk(data)
        self.assertEqual(result['label'], 'MEDIUM')
        self.assertEqual(result['score'], 3)
        
    def test_high_risk_score(self):
        # Age 80 (+2), HR 125 (+2), BP 85 (+2) = Score 6 -> HIGH
        data = {
            'age': 80, 'heart_rate': 125, 'systolic_bp': 85, 'spo2': 98,
            'temperature': 37.0, 'respiratory_rate': 16,
            'history': [], 'er_visits': 0, 'lab_issues': []
        }
        result = calculate_risk(data)
        self.assertEqual(result['label'], 'HIGH')
        self.assertTrue(result['score'] >= 6)

    def test_critical_trigger_spo2(self):
        # Low SPO2 (<85) should trigger HIGH regardless of score
        data = {
            'age': 30, 'heart_rate': 70, 'systolic_bp': 120, 'spo2': 80, # Critical
            'temperature': 37.0, 'respiratory_rate': 16,
            'history': [], 'er_visits': 0, 'lab_issues': []
        }
        result = calculate_risk(data)
        self.assertEqual(result['label'], 'HIGH')
        self.assertTrue("CRITICAL ESCALATION" in result['notes'][0])

    def test_critical_trigger_bp(self):
         # Low BP (<80) should trigger HIGH regardless of score
        data = {
            'age': 30, 'heart_rate': 70, 'systolic_bp': 75, # Critical
            'spo2': 98, 'temperature': 37.0, 'respiratory_rate': 16,
            'history': [], 'er_visits': 0, 'lab_issues': []
        }
        result = calculate_risk(data)
        self.assertEqual(result['label'], 'HIGH')

    def test_history_parsing(self):
        data = {
            'age': 30, 'heart_rate': 70, 'systolic_bp': 120, 'spo2': 98,
            'temperature': 37.0, 'respiratory_rate': 16,
            'history': ['Diabetes Type 2', 'Hypertension'], 
            'er_visits': 0, 'lab_issues': []
        }
        result = calculate_risk(data)
        # Diabetes +1, Hypertension +1 = 2
        self.assertEqual(result['score'], 2)

class TestPDFParsing(unittest.TestCase):
    def setUp(self):
        self.test_pdf = "test_gen.pdf"
        c = canvas.Canvas(self.test_pdf)
        c.drawString(100, 750, "Patient Name: John Test")
        c.drawString(100, 730, "Age: 45")
        c.drawString(100, 710, "Gender: Male")
        c.drawString(100, 690, "Heart Rate: 80 bpm")
        c.drawString(100, 670, "BP: 120/80 mmHg")
        c.drawString(100, 650, "SpO2: 98%")
        c.drawString(100, 630, "Temp: 37.0 C")
        c.drawString(100, 610, "Resp: 18")
        c.drawString(100, 590, "History: Diabetes.")
        c.save()

    def tearDown(self):
        if os.path.exists(self.test_pdf):
            os.remove(self.test_pdf)

    def test_extract_data(self):
        data = extract_data_from_pdf(self.test_pdf)
        self.assertEqual(data.get('name'), "John Test")
        self.assertEqual(data.get('age'), 45)
        self.assertEqual(data.get('heart_rate'), 80)
        self.assertEqual(data.get('systolic_bp'), 120)
        self.assertEqual(data.get('diastolic_bp'), 80)
        self.assertIn('Diabetes', data.get('history', []))


class TestWebApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_dashboard_load(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_add_patient(self):
        response = self.app.post('/add', data={
            'name': 'Test User',
            'age': '50',
            'gender': 'Male',
            'heart_rate': '80',
            'systolic_bp': '120',
            'diastolic_bp': '80',
            'spo2': '99',
            'temperature': '37.0',
            'respiratory_rate': '18',
            'er_visits': '0',
            'history': 'Diabetes',
            'lab_issues': '',
            'notes': 'Test Note'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test User', response.data)
        
        with app.app_context():
            p = Patient.query.first()
            self.assertIsNotNone(p)
            self.assertEqual(p.name, 'Test User')
            self.assertEqual(p.notes, 'Test Note')
            # Verify Risk Calculation happened
            # Age 50 (0) + Diabetes (1) = 1 -> LOW
            self.assertEqual(p.risk_label, 'LOW')

    def test_update_patient_risk_change(self):
         # Create initial patient
        with app.app_context():
            p = Patient(
                name="Update Test", age=50, gender="F",
                heart_rate=80, systolic_bp=120, diastolic_bp=80, spo2=99,
                temperature=37.0, respiratory_rate=18, er_visits=0,
                history="[]", lab_issues="[]", notes="",
                risk_score=0, risk_label="LOW", risk_notes="[]"
            )
            db.session.add(p)
            db.session.commit()
            p_id = p.id

        # Update with critical values
        response = self.app.post(f'/update/{p_id}', data={
            'heart_rate': '150', # Critical High
            'systolic_bp': '120',
            'diastolic_bp': '80',
            'spo2': '99',
            'temperature': '37.0',
            'respiratory_rate': '18',
            'er_visits': '0',
            'notes': 'New Note'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        with app.app_context():
            p = Patient.query.get(p_id)
            self.assertEqual(p.heart_rate, 150)
            self.assertEqual(p.risk_label, 'HIGH')
            self.assertEqual(p.notes, 'New Note')


if __name__ == '__main__':
    unittest.main()
