
import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define models
class Consultant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    registration_number = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    parent_name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    consultant_id = db.Column(db.Integer, db.ForeignKey('consultant.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    consultant_id = db.Column(db.Integer, db.ForeignKey('consultant.id'), nullable=False)
    weight = db.Column(db.Float)
    status = db.Column(db.String(20), default='waiting')
    visit_date = db.Column(db.Date, default=datetime.utcnow().date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

def setup_database():
    print("Creating database...")
    with app.app_context():
        db.create_all()
        
        # Add default consultants
        if not Consultant.query.first():
            consultants = [
                Consultant(name="Dr. Ajitha", specialization="Pediatric Allergy"),
                Consultant(name="Dr. Galle", specialization="Asthma Specialist")
            ]
            for consultant in consultants:
                db.session.add(consultant)
            db.session.commit()
            print("Default consultants added")
        
        print("Database setup complete!")

if __name__ == "__main__":
    setup_database()
