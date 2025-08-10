
from flask import render_template, request, jsonify, redirect, url_for, session, flash
from app import app, db
from models import Patient, Consultant, Visit
from datetime import datetime, date
import json

@app.route('/')
def index():
    return redirect(url_for('reception'))

@app.route('/queue_management')
def queue_management():
    return render_template('queue_management.html')

@app.route('/reception')
def reception():
    return redirect(url_for('receptionist'))

@app.route('/receptionist')
def receptionist():
    consultants = Consultant.query.all()
    today = date.today()
    
    # Get today's visits grouped by status
    waiting_visits = db.session.query(Visit).join(Patient).filter(
        db.func.date(Visit.visit_date) == today,
        Visit.status == 'waiting'
    ).order_by(Visit.visit_date.asc()).all()
    
    completed_visits = db.session.query(Visit).join(Patient).filter(
        db.func.date(Visit.visit_date) == today,
        Visit.status == 'completed'
    ).order_by(Visit.completed_at.desc()).all()
    
    total_waiting = len(waiting_visits)
    total_completed = len(completed_visits)
    
    return render_template('receptionist.html', 
                         consultants=consultants,
                         waiting_visits=waiting_visits,
                         completed_visits=completed_visits,
                         total_waiting=total_waiting,
                         total_completed=total_completed)

@app.route('/consultant')
def consultant():
    consultants = Consultant.query.all()
    return render_template('consultant_simple.html', consultants=consultants)

@app.route('/api/patients')
def get_patients():
    consultant_id = request.args.get('consultant_id', type=int)
    
    if consultant_id:
        patients = Patient.query.filter_by(consultant_id=consultant_id).all()
    else:
        patients = Patient.query.all()
    
    patient_list = []
    for patient in patients:
        # Get current visit
        current_visit = Visit.query.filter_by(patient_id=patient.id, status='waiting').first()
        
        patient_data = {
            'id': patient.id,
            'registration_number': patient.registration_number,
            'name': patient.name,
            'age': patient.age,
            'parent_name': patient.parent_name,
            'email': patient.email,
            'phone': patient.phone,
            'consultant_id': patient.consultant_id,
            'consultant_name': patient.consultant.name if patient.consultant else 'Not Assigned',
            'current_visit': {
                'id': current_visit.id if current_visit else None,
                'weight': current_visit.weight if current_visit else None,
                'status': current_visit.status if current_visit else 'no_visit',
                'created_at': current_visit.created_at.isoformat() if current_visit else None
            }
        }
        patient_list.append(patient_data)
    
    return jsonify(patient_list)

@app.route('/api/register_patient', methods=['POST'])
def register_patient():
    data = request.json
    
    # Generate registration number
    today = datetime.now()
    date_prefix = today.strftime('%d%m%y')
    
    # Find the next number for today
    existing_count = Patient.query.filter(
        Patient.registration_number.like(f'{date_prefix}%')
    ).count()
    next_number = existing_count + 1
    registration_number = f'{date_prefix}{next_number:03d}'
    
    # Create patient
    patient = Patient(
        registration_number=registration_number,
        name=data['name'],
        age=data.get('age'),
        parent_name=data.get('parent_name'),
        email=data.get('email'),
        phone=data.get('phone'),
        consultant_id=data.get('consultant_id')
    )
    
    db.session.add(patient)
    db.session.commit()
    
    # Create initial visit
    visit = Visit(
        patient_id=patient.id,
        weight=data.get('weight'),
        status='waiting'
    )
    
    db.session.add(visit)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'patient_id': patient.id,
        'registration_number': registration_number,
        'visit_id': visit.id
    })

@app.route('/api/complete_consultation', methods=['POST'])
def complete_consultation():
    data = request.json
    visit_id = data.get('visit_id')
    
    visit = Visit.query.get(visit_id)
    if visit:
        visit.status = 'completed'
        visit.completed_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Visit not found'})

@app.route('/api/update_patient', methods=['POST'])
def update_patient():
    data = request.json
    patient_id = data.get('patient_id')
    
    patient = Patient.query.get(patient_id)
    if patient:
        patient.name = data.get('name', patient.name)
        patient.age = data.get('age', patient.age)
        patient.parent_name = data.get('parent_name', patient.parent_name)
        patient.email = data.get('email', patient.email)
        patient.phone = data.get('phone', patient.phone)
        patient.consultant_id = data.get('consultant_id', patient.consultant_id)
        
        # Update current visit weight if provided
        if 'weight' in data:
            current_visit = Visit.query.filter_by(patient_id=patient.id, status='waiting').first()
            if current_visit:
                current_visit.weight = data['weight']
        
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Patient not found'})

@app.route('/api/consultants')
def get_consultants():
    consultants = Consultant.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'specialization': c.specialization
    } for c in consultants])

@app.route('/api/waiting_patients')
def get_waiting_patients():
    consultant_id = request.args.get('consultant_id', type=int)
    
    query = db.session.query(Patient, Visit).join(Visit).filter(Visit.status == 'waiting')
    
    if consultant_id:
        query = query.filter(Patient.consultant_id == consultant_id)
    
    results = query.order_by(Visit.created_at.asc()).all()
    
    patients = []
    for patient, visit in results:
        patients.append({
            'id': patient.id,
            'registration_number': patient.registration_number,
            'name': patient.name,
            'age': patient.age,
            'parent_name': patient.parent_name,
            'consultant_name': patient.consultant.name if patient.consultant else 'Not Assigned',
            'weight': visit.weight,
            'visit_id': visit.id,
            'waiting_time': (datetime.utcnow() - visit.created_at).total_seconds() / 60  # minutes
        })
    
    return jsonify(patients)

@app.route('/print_patient/<int:patient_id>')
def print_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    current_visit = Visit.query.filter_by(patient_id=patient.id, status='waiting').first()
    
    return render_template('print_patient.html', 
                         patient=patient, 
                         visit=current_visit,
                         print_date=datetime.now())

@app.route('/report')
def report():
    today = date.today()
    
    # Get today's visits
    today_visits = db.session.query(Patient, Visit).join(Visit).filter(
        db.func.date(Visit.created_at) == today
    ).order_by(Visit.created_at.desc()).all()
    
    # Statistics
    total_visits = len(today_visits)
    waiting_count = sum(1 for _, visit in today_visits if visit.status == 'waiting')
    completed_count = sum(1 for _, visit in today_visits if visit.status == 'completed')
    
    # Group by consultant
    consultant_stats = {}
    for patient, visit in today_visits:
        consultant_name = patient.consultant.name if patient.consultant else 'Unassigned'
        if consultant_name not in consultant_stats:
            consultant_stats[consultant_name] = {'waiting': 0, 'completed': 0, 'total': 0}
        
        consultant_stats[consultant_name][visit.status] += 1
        consultant_stats[consultant_name]['total'] += 1
    
    return render_template('report.html',
                         today_visits=today_visits,
                         total_visits=total_visits,
                         waiting_count=waiting_count,
                         completed_count=completed_count,
                         consultant_stats=consultant_stats,
                         report_date=today)

@app.route('/print_daily_summary')
def print_daily_summary():
    today = date.today()
    
    # Get today's visits
    today_visits = db.session.query(Patient, Visit).join(Visit).filter(
        db.func.date(Visit.created_at) == today
    ).order_by(Visit.created_at.asc()).all()
    
    # Statistics
    total_visits = len(today_visits)
    waiting_count = sum(1 for _, visit in today_visits if visit.status == 'waiting')
    completed_count = sum(1 for _, visit in today_visits if visit.status == 'completed')
    
    return render_template('print_daily_summary.html',
                         today_visits=today_visits,
                         total_visits=total_visits,
                         waiting_count=waiting_count,
                         completed_count=completed_count,
                         report_date=today)

@app.route('/admin_login')
def admin_login():
    return render_template('admin_login.html')

@app.route('/admin_panel', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'drajitha' and password == 'ajith@galle':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash('Invalid credentials')
            return redirect(url_for('admin_login'))
    
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    consultants = Consultant.query.all()
    patients = Patient.query.all()
    
    return render_template('admin_panel.html', consultants=consultants, patients=patients)

@app.route('/admin/add_consultant', methods=['POST'])
def add_consultant():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'Not authorized'})
    
    data = request.json
    consultant = Consultant(
        name=data['name'],
        specialization=data.get('specialization', '')
    )
    
    db.session.add(consultant)
    db.session.commit()
    
    return jsonify({'success': True, 'consultant_id': consultant.id})

@app.route('/admin/delete_patient/<int:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'Not authorized'})
    
    patient = Patient.query.get(patient_id)
    if patient:
        db.session.delete(patient)
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Patient not found'})

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))
