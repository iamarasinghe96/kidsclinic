from app import db
from datetime import datetime
from sqlalchemy import func
import pytz

# Sri Lankan timezone
SL_TZ = pytz.timezone('Asia/Colombo')

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    registration_number = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(10), nullable=True, default='')  # Baby, Mr., Mrs., Miss, Rev.
    full_name = db.Column(db.String(100), nullable=False)
    parent_name = db.Column(db.String(100), nullable=True)  # Made optional
    date_of_birth = db.Column(db.Date, nullable=False)
    address = db.Column(db.Text, nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    gender = db.Column(db.String(10), nullable=False)
    consultant_id = db.Column(db.Integer, db.ForeignKey('consultant.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(SL_TZ).replace(tzinfo=None))
    
    # Relationships
    consultant = db.relationship('Consultant', backref='patients')
    visits = db.relationship('Visit', backref='patient', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Patient {self.registration_number}: {self.display_name}>'
    
    @property
    def display_name(self):
        """Return the full display name with title"""
        if self.title and self.title.strip():
            return f"{self.title} {self.full_name}"
        return self.full_name
    
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
    # color = db.Column(db.String(7), default='#6c757d')  # Temporarily commented out for migration
    consultation_fee = db.Column(db.Float, default=0.0, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(SL_TZ).replace(tzinfo=None))
    
    def __repr__(self):
        return f'<Consultant {self.name}>'

class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    consultant_id = db.Column(db.Integer, db.ForeignKey('consultant.id'), nullable=False)
    visit_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(SL_TZ).replace(tzinfo=None))
    status = db.Column(db.String(20), nullable=False, default='waiting')  # waiting, completed, incomplete, completed_archived
    completed_at = db.Column(db.DateTime)
    weight_kg = db.Column(db.Float, nullable=True)  # Patient weight in kg at time of visit
    
    # Relationships
    consultant = db.relationship('Consultant', backref='visits')
    
    def __repr__(self):
        return f'<Visit {self.id}: Patient {self.patient_id} - {self.status}>'
    
    def mark_completed(self):
        """Mark this visit as completed"""
        self.status = 'completed'
        self.completed_at = datetime.now(SL_TZ).replace(tzinfo=None)
        db.session.commit()
