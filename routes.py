from flask import render_template, request, jsonify, redirect, url_for, session, flash
from app import app, db
from models import Patient, Consultant, Visit
from datetime import datetime, date
import json

@app.route('/')
def index():
    return redirect(url_for('receptionist'))

@app.route('/receptionist')
def receptionist():
    consultants = Consultant.query.all()
    return render_template('receptionist.html', consultants=consultants)

@app.route('/register_patient', methods=['POST'])
def register_patient():
    try:
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
            full_name=request.form['full_name'],
            date_of_birth=datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date(),
            gender=request.form['gender'],
            parent_name=request.form.get('parent_name'),
            contact_number=request.form['contact_number'],
            email=request.form.get('email'),
            address=request.form['address'],
            consultant_id=request.form['consultant_id']
        )

        db.session.add(patient)
        db.session.commit()

        # Create initial visit
        visit = Visit(
            patient_id=patient.id,
            consultant_id=patient.consultant_id,
            weight_kg=float(request.form['weight_kg']) if request.form.get('weight_kg') else None,
            status='waiting'
        )

        db.session.add(visit)
        db.session.commit()

        flash(f'Patient {patient.full_name} registered successfully with number {registration_number}', 'success')
        return redirect(url_for('receptionist'))

    except Exception as e:
        db.session.rollback()
        flash('Error registering patient', 'error')
        return redirect(url_for('receptionist'))

@app.route('/search_patients')
def search_patients():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])

    patients = Patient.query.filter(
        db.or_(
            Patient.full_name.contains(query),
            Patient.registration_number.contains(query),
            Patient.contact_number.contains(query)
        )
    ).limit(10).all()

    patient_list = []
    for patient in patients:
        patient_data = {
            'id': patient.id,
            'full_name': patient.full_name,
            'registration_number': patient.registration_number,
            'date_of_birth': patient.date_of_birth.strftime('%Y-%m-%d'),
            'contact_number': patient.contact_number,
            'consultant_name': patient.consultant.name if patient.consultant else 'Not Assigned'
        }
        patient_list.append(patient_data)

    return jsonify(patient_list)

@app.route('/get_patient_details_by_id/<int:patient_id>')
def get_patient_details_by_id(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    return jsonify({
        'id': patient.id,
        'full_name': patient.full_name,
        'registration_number': patient.registration_number,
        'date_of_birth': patient.date_of_birth.strftime('%Y-%m-%d'),
        'contact_number': patient.contact_number,
        'consultant_name': patient.consultant.name if patient.consultant else 'Not Assigned'
    })

@app.route('/register_returning_patient', methods=['POST'])
def register_returning_patient():
    try:
        patient_id = request.form.get('patient_id')
        weight_kg = request.form.get('weight_kg')

        patient = Patient.query.get_or_404(patient_id)

        # Create new visit
        visit = Visit(
            patient_id=patient.id,
            consultant_id=patient.consultant_id,
            weight_kg=float(weight_kg) if weight_kg else None,
            status='waiting'
        )

        db.session.add(visit)
        db.session.commit()

        flash(f'Patient {patient.full_name} added to today\'s queue', 'success')
        return redirect(url_for('receptionist'))

    except Exception as e:
        db.session.rollback()
        flash('Error registering returning patient', 'error')
        return redirect(url_for('receptionist'))