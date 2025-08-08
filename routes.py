from flask import render_template, request, redirect, url_for, flash, jsonify, make_response
from datetime import datetime, date
from sqlalchemy import or_, func
from app import app, db
from models import Patient, Consultant, Visit
import logging
import io
import csv

def generate_registration_number():
    """Generate a unique registration number"""
    today = datetime.now()
    prefix = f"REG{today.year}{today.month:02d}"
    
    # Find the last registration number for today
    last_patient = Patient.query.filter(
        Patient.registration_number.like(f"{prefix}%")
    ).order_by(Patient.registration_number.desc()).first()
    
    if last_patient:
        # Extract the sequence number and increment
        last_seq = int(last_patient.registration_number[-4:])
        new_seq = last_seq + 1
    else:
        new_seq = 1
    
    return f"{prefix}{new_seq:04d}"

@app.route('/')
def index():
    return redirect(url_for('reception'))

@app.route('/reception', methods=['GET', 'POST'])
def reception():
    consultants = Consultant.query.all()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'new_patient':
            # Handle new patient registration
            try:
                registration_number = generate_registration_number()
                
                patient = Patient(
                    registration_number=registration_number,
                    full_name=request.form['full_name'],
                    date_of_birth=datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date(),
                    address=request.form['address'],
                    contact_number=request.form['contact_number'],
                    gender=request.form['gender'],
                    consultant_id=int(request.form['consultant_id'])
                )
                
                db.session.add(patient)
                db.session.commit()
                
                # Create a visit record for today
                visit = Visit(
                    patient_id=patient.id,
                    consultant_id=patient.consultant_id,
                    status='waiting'
                )
                db.session.add(visit)
                db.session.commit()
                
                flash(f'Patient registered successfully! Registration Number: {registration_number}', 'success')
                logging.info(f"New patient registered: {registration_number}")
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error registering patient: {str(e)}', 'error')
                logging.error(f"Error registering patient: {str(e)}")
        
        elif action == 'returning_patient':
            # Handle returning patient
            reg_number = request.form['registration_number']
            patient = Patient.query.filter_by(registration_number=reg_number).first()
            
            if patient:
                # Update consultant if provided
                if request.form.get('consultant_id'):
                    patient.consultant_id = int(request.form['consultant_id'])
                    db.session.commit()
                
                # Create a new visit record
                visit = Visit(
                    patient_id=patient.id,
                    consultant_id=patient.consultant_id,
                    status='waiting'
                )
                db.session.add(visit)
                db.session.commit()
                
                flash(f'Welcome back, {patient.full_name}! Visit registered.', 'success')
                logging.info(f"Returning patient visit: {reg_number}")
            else:
                flash('Patient not found with this registration number.', 'error')
    
    return render_template('reception.html', consultants=consultants)

@app.route('/search_patients')
def search_patients():
    query = request.args.get('query', '').strip()
    
    if not query:
        return jsonify([])
    
    # Search by name or contact number
    patients = Patient.query.filter(
        or_(
            Patient.full_name.ilike(f'%{query}%'),
            Patient.contact_number.like(f'%{query}%')
        )
    ).limit(10).all()
    
    results = []
    for patient in patients:
        results.append({
            'registration_number': patient.registration_number,
            'full_name': patient.full_name,
            'contact_number': patient.contact_number,
            'consultant': patient.consultant.name
        })
    
    return jsonify(results)

@app.route('/get_patient/<reg_number>')
def get_patient(reg_number):
    patient = Patient.query.filter_by(registration_number=reg_number).first()
    if patient:
        return jsonify({
            'full_name': patient.full_name,
            'date_of_birth': patient.date_of_birth.strftime('%Y-%m-%d'),
            'address': patient.address,
            'contact_number': patient.contact_number,
            'gender': patient.gender,
            'consultant_id': patient.consultant_id
        })
    return jsonify({'error': 'Patient not found'}), 404

@app.route('/consultant')
def consultant():
    consultants = Consultant.query.all()
    consultant_id = request.args.get('consultant_id', type=int)
    
    waiting_visits = []
    completed_visits = []
    
    if consultant_id:
        # Get today's visits for this consultant
        today = date.today()
        waiting_visits = Visit.query.join(Patient).filter(
            Visit.consultant_id == consultant_id,
            Visit.status == 'waiting',
            func.date(Visit.visit_date) == today
        ).order_by(Visit.visit_date.asc()).all()
        
        completed_visits = Visit.query.join(Patient).filter(
            Visit.consultant_id == consultant_id,
            Visit.status == 'completed',
            func.date(Visit.visit_date) == today
        ).order_by(Visit.completed_at.desc()).all()
    
    return render_template('consultant.html', 
                         consultants=consultants,
                         waiting_visits=waiting_visits,
                         completed_visits=completed_visits,
                         selected_consultant_id=consultant_id)

@app.route('/get_patient_details/<reg_number>')
def get_patient_details(reg_number):
    patient = Patient.query.filter_by(registration_number=reg_number).first()
    if patient:
        recent_visits = patient.get_recent_visits()
        visit_dates = [visit.visit_date.strftime('%Y-%m-%d') for visit in recent_visits]
        
        return jsonify({
            'registration_number': patient.registration_number,
            'full_name': patient.full_name,
            'age': patient.age,
            'gender': patient.gender,
            'date_of_birth': patient.date_of_birth.strftime('%Y-%m-%d'),
            'recent_visits': visit_dates
        })
    return jsonify({'error': 'Patient not found'}), 404

@app.route('/complete_consultation', methods=['POST'])
def complete_consultation():
    reg_number = request.form['registration_number']
    patient = Patient.query.filter_by(registration_number=reg_number).first()
    
    if patient:
        # Find today's waiting visit for this patient
        today = date.today()
        visit = Visit.query.filter(
            Visit.patient_id == patient.id,
            Visit.status == 'waiting',
            func.date(Visit.visit_date) == today
        ).first()
        
        if visit:
            visit.mark_completed()
            flash(f'Consultation completed for {patient.full_name}', 'success')
        else:
            flash('No active visit found for this patient', 'error')
    else:
        flash('Patient not found', 'error')
    
    return redirect(url_for('consultant', consultant_id=request.form.get('consultant_id')))

@app.route('/report', methods=['GET', 'POST'])
def report():
    consultants = Consultant.query.all()
    report_data = None
    
    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        consultant_id = request.form.get('consultant_id')
        
        # Build query for completed visits within date range
        query = Visit.query.join(Patient).filter(
            Visit.status == 'completed',
            func.date(Visit.visit_date) >= start_date,
            func.date(Visit.visit_date) <= end_date
        )
        
        # Add consultant filter if specified
        if consultant_id and consultant_id != 'all':
            query = query.filter(Visit.consultant_id == int(consultant_id))
        
        visits = query.order_by(Visit.visit_date.asc()).all()
        
        # Get consultant name for report
        selected_consultant = None
        if consultant_id and consultant_id != 'all':
            selected_consultant = Consultant.query.get(int(consultant_id))
        
        report_data = {
            'start_date': start_date,
            'end_date': end_date,
            'total_consultations': len(visits),
            'visits': visits,
            'selected_consultant': selected_consultant,
            'consultant_id': consultant_id
        }
    
    return render_template('report.html', report_data=report_data, consultants=consultants)

@app.route('/download_report_csv')
def download_report_csv():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    consultant_id = request.args.get('consultant_id')
    
    if not start_date or not end_date:
        flash('Invalid date parameters', 'error')
        return redirect(url_for('report'))
    
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Build query for completed visits within date range
    query = Visit.query.join(Patient).filter(
        Visit.status == 'completed',
        func.date(Visit.visit_date) >= start_date,
        func.date(Visit.visit_date) <= end_date
    )
    
    # Add consultant filter if specified
    if consultant_id and consultant_id != 'all':
        query = query.filter(Visit.consultant_id == int(consultant_id))
    
    visits = query.order_by(Visit.visit_date.asc()).all()
    
    # Create CSV data
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Registration Number',
        'Patient Name', 
        'Consultant',
        'Visit Date',
        'Visit Time',
        'Completed Time'
    ])
    
    # Write data rows
    for visit in visits:
        writer.writerow([
            visit.patient.registration_number,
            visit.patient.full_name,
            visit.consultant.name,
            visit.visit_date.strftime('%Y-%m-%d'),
            visit.visit_date.strftime('%H:%M'),
            visit.completed_at.strftime('%H:%M') if visit.completed_at else '-'
        ])
    
    # Determine filename suffix
    consultant_suffix = ""
    if consultant_id and consultant_id != 'all':
        consultant = Consultant.query.get(int(consultant_id))
        if consultant:
            consultant_suffix = f"_{consultant.name.replace(' ', '_')}"
    
    # Prepare response
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=consultation_report_{start_date}_to_{end_date}{consultant_suffix}.csv'
    
    return response
