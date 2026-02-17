import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from risk_engine import calculate_risk

class TestRiskEngine(unittest.TestCase):

    def test_sarah_jenkins_case(self):
        data = {
            'age': 72,              
            'heart_rate': 102,      
            'systolic_bp': 110,     
            'spo2': 91,             
            'temperature': 36.8,    
            'respiratory_rate': 20, 
            'history': ['Diabetes', 'COPD'], 
            'er_visits': 1,         
            'lab_issues': ['Elevated WBC'] 
        }
        
        result = calculate_risk(data)
        
        print(f"\nTest Sarah Jenkins: Score {result['score']}, Label {result['label']}")
        self.assertEqual(result['score'], 6)
        self.assertEqual(result['label'], "HIGH")

    def test_critical_escalation(self):
        data = {
            'age': 30,
            'heart_rate': 70,
            'systolic_bp': 120,
            'spo2': 84,
            'temperature': 37.0,
        }
        
        result = calculate_risk(data)
        
        print(f"Test Critical Escalation: Score {result['score']}, Label {result['label']}")
        self.assertEqual(result['label'], "HIGH")
        self.assertIn("Critical: SpO2 84% (<85%)", str(result['notes']))

    def test_healthy_patient(self):
        data = {
            'age': 25,
            'heart_rate': 70,
            'systolic_bp': 120,
            'spo2': 99,
            'temperature': 37.0,
        }
        result = calculate_risk(data)
        self.assertEqual(result['score'], 0)
        self.assertEqual(result['label'], "LOW")

    def test_unrecognized_condition(self):
        data = {
            'age': 30,
            'heart_rate': 70,
            'systolic_bp': 120,
            'spo2': 98,
            'temperature': 37.0,
            'history': ['Diabetes', 'Unknown Ailment'],
        }
        result = calculate_risk(data)
        self.assertEqual(result['score'], 1) 
        self.assertIn("Unknown Ailment", result['unrecognized_conditions'])
        self.assertIn("WARNING: Unrecognized condition 'Unknown Ailment'", result['notes'])

    def test_new_valid_condition(self):
        data = {
            'age': 30,
            'heart_rate': 70,
            'systolic_bp': 120,
            'spo2': 98,
            'temperature': 37.0,
            'history': ['Stroke', 'Asthma'],
        }
        result = calculate_risk(data)
        self.assertEqual(result['score'], 2) 
        self.assertIn("History: Stroke", result['notes'])
        self.assertIn("History: Asthma", result['notes'])

if __name__ == '__main__':
    unittest.main()