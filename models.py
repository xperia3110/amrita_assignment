from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10))
    admission_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Clinical Parameters
    heart_rate = db.Column(db.Integer)
    systolic_bp = db.Column(db.Integer)
    diastolic_bp = db.Column(db.Integer)
    spo2 = db.Column(db.Integer)
    temperature = db.Column(db.Float)
    respiratory_rate = db.Column(db.Integer)
    
    # Storing lists as JSON strings because SQLite is simple
    history = db.Column(db.Text, default="[]") 
    lab_issues = db.Column(db.Text, default="[]")
    er_visits = db.Column(db.Integer, default=0)
    
    # System Calculated Risk (Read-Only for Users)
    risk_score = db.Column(db.Integer, default=0)
    risk_label = db.Column(db.String(20), default="LOW") # LOW, MEDIUM, HIGH
    risk_notes = db.Column(db.Text, default="")
    
    # Clinical Notes
    notes = db.Column(db.Text, default="")

    # Relationship to Logs
    logs = db.relationship('AuditLog', backref='patient', lazy=True, cascade="all, delete-orphan")

    @property
    def history_list(self):
        try:
            items = json.loads(self.history) if self.history else []
            return [i for i in items if i and i.strip()]
        except:
            return []

    @property
    def lab_issues_list(self):
        try:
            items = json.loads(self.lab_issues) if self.lab_issues else []
            return [i for i in items if i and i.strip()]
        except:
            return []

    @property
    def risk_notes_list(self):
        try:
            items = json.loads(self.risk_notes) if self.risk_notes else []
            return [i for i in items if i and i.strip()]
        except:
            return []

    def to_dict(self):
        """Helper to convert object to dict for the Risk Engine"""
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'heart_rate': self.heart_rate,
            'systolic_bp': self.systolic_bp,
            'diastolic_bp': self.diastolic_bp,
            'spo2': self.spo2,
            'temperature': self.temperature,
            'respiratory_rate': self.respiratory_rate,
            'history': self.history_list,
            'lab_issues': self.lab_issues_list,
            'er_visits': self.er_visits,
            'risk_score': self.risk_score,
            'er_visits': self.er_visits,
            'risk_score': self.risk_score,
            'risk_label': self.risk_label,
            'notes': self.notes
        }

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # What changed?
    field_changed = db.Column(db.String(50))
    old_value = db.Column(db.String(200))
    new_value = db.Column(db.String(200))
    
    # Did the Risk Level change?
    risk_change = db.Column(db.String(100)) # e.g. "LOW -> HIGH"