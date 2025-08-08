from app import db
from datetime import datetime
from sqlalchemy import func

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    registration_number = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    address = db.Column(db.Text, nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    consultant_id = db.Column(db.Integer, db.ForeignKey('consultant.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    consultant = db.relationship('Consultant', backref='patients')
    visits = db.relationship('Visit', backref='patient', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Patient {self.registration_number}: {self.full_name}>'
    
    @property
    def age(self):
        """Calculate current age from date of birth"""
        today = datetime.now().date()
        born = self.date_of_birth
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    
    def get_recent_visits(self, limit=5):
        """Get the most recent visits for this patient"""
        return Visit.query.filter_by(patient_id=self.id)\
                          .filter(Visit.status == 'completed')\
                          .order_by(Visit.visit_date.desc())\
                          .limit(limit).all()

class Consultant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Consultant {self.name}>'

class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    consultant_id = db.Column(db.Integer, db.ForeignKey('consultant.id'), nullable=False)
    visit_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='waiting')  # waiting, completed
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    consultant = db.relationship('Consultant', backref='visits')
    
    def __repr__(self):
        return f'<Visit {self.id}: Patient {self.patient_id} - {self.status}>'
    
    def mark_completed(self):
        """Mark this visit as completed"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        db.session.commit()
