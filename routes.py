from flask import render_template, request, redirect, url_for, flash, jsonify, make_response, session
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
    return redirect(url_for('receptionist'))

@app.route('/queue_management')
def queue_management():
    today = date.today()
    
    # Get all consultants
    consultants = Consultant.query.all()
    
    # Get today's waiting visits
    waiting_visits = Visit.query.join(Patient).join(Consultant).filter(
        Visit.status == 'waiting',
        func.date(Visit.visit_date) == today
    ).order_by(Visit.visit_date.asc()).all()
    
    # Get today's completed visits
    completed_visits = Visit.query.join(Patient).join(Consultant).filter(
        Visit.status == 'completed',
        func.date(Visit.visit_date) == today
    ).order_by(Visit.completed_at.desc()).all()
    
    # Calculate totals
    total_waiting = len(waiting_visits)
    total_completed = len(completed_visits)
    total_patients_today = total_waiting + total_completed
    
    return render_template('queue_management.html',
                         waiting_visits=waiting_visits,
                         completed_visits=completed_visits,
                         consultants=consultants,
                         total_waiting=total_waiting,
                         total_completed=total_completed,
                         total_patients_today=total_patients_today)

@app.route('/receptionist')
def receptionist():
    consultants = Consultant.query.all()
    return render_template('receptionist_simple.html', consultants=consultants)

# Consultant route moved to avoid conflict

@app.route('/consultant/<int:consultant_id>')
def consultant_view(consultant_id):
    consultant = Consultant.query.get_or_404(consultant_id)
    
    # Get today's visits for this specific consultant only
    today = date.today()
    waiting_visits = Visit.query.join(Patient).filter(
        Visit.consultant_id == consultant_id,
        Visit.status == 'waiting',
        func.date(Visit.visit_date) == today
    ).order_by(Visit.visit_date.asc()).limit(10).all()
    
    completed_visits = Visit.query.join(Patient).filter(
        Visit.consultant_id == consultant_id,
        Visit.status == 'completed',
        func.date(Visit.visit_date) == today
    ).order_by(Visit.completed_at.desc()).limit(8).all()
    
    total_waiting = Visit.query.filter(
        Visit.consultant_id == consultant_id,
        Visit.status == 'waiting',
        func.date(Visit.visit_date) == today
    ).count()
    
    total_completed = Visit.query.filter(
        Visit.consultant_id == consultant_id,
        Visit.status == 'completed',
        func.date(Visit.visit_date) == today
    ).count()
    
    # Generate time-based greeting
    from datetime import datetime
    import pytz
    
    # Sri Lankan timezone
    lk_tz = pytz.timezone('Asia/Colombo')
    current_time = datetime.now(lk_tz)
    hour = current_time.hour
    
    if 5 <= hour < 12:
        greeting = "Good Morning"
    elif 12 <= hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    
    return render_template('consultant_simple.html', 
                         waiting_visits=waiting_visits,
                         completed_visits=completed_visits,
                         selected_consultant=consultant,
                         selected_consultant_id=consultant_id,
                         greeting=greeting,
                         total_waiting=total_waiting,
                         total_completed=total_completed)

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
                    parent_name=request.form.get('parent_name', ''),
                    date_of_birth=datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date(),
                    address=request.form['address'],
                    contact_number=request.form['contact_number'],
                    email=request.form.get('email', ''),
                    gender=request.form['gender'],
                    consultant_id=int(request.form['consultant_id'])
                )
                
                db.session.add(patient)
                db.session.commit()
                
                # Create a visit record for today with weight
                visit = Visit(
                    patient_id=patient.id,
                    consultant_id=patient.consultant_id,
                    status='waiting',
                    weight_kg=float(request.form['weight_kg']) if request.form.get('weight_kg') else None
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
                
                # Create a new visit record with weight
                visit = Visit(
                    patient_id=patient.id,
                    consultant_id=patient.consultant_id,
                    status='waiting',
                    weight_kg=float(request.form['weight_kg']) if request.form.get('weight_kg') else None
                )
                db.session.add(visit)
                db.session.commit()
                
                flash(f'Welcome back, {patient.full_name}! Visit registered.', 'success')
                logging.info(f"Returning patient visit: {reg_number}")
            else:
                flash('Patient not found with this registration number.', 'error')
    
    return render_template('reception.html', consultants=consultants)

# New routes for enhanced patient management
@app.route('/search_patients')
def search_patients():
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify([])
    
    # Search by name or contact number or registration number
    patients = Patient.query.join(Consultant).filter(
        db.or_(
            Patient.full_name.ilike(f'%{query}%'),
            Patient.contact_number.ilike(f'%{query}%'),
            Patient.registration_number.ilike(f'%{query}%')
        )
    ).limit(10).all()
    
    results = []
    for patient in patients:
        results.append({
            'id': patient.id,
            'full_name': patient.full_name,
            'registration_number': patient.registration_number,
            'date_of_birth': patient.date_of_birth.strftime('%Y-%m-%d'),
            'contact_number': patient.contact_number,
            'consultant_name': patient.consultant.name
        })
    
    return jsonify(results)

@app.route('/get_patient_details_by_id/<int:patient_id>')
def get_patient_details_by_id(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    return jsonify({
        'id': patient.id,
        'registration_number': patient.registration_number,
        'full_name': patient.full_name,
        'date_of_birth': patient.date_of_birth.strftime('%Y-%m-%d'),
        'contact_number': patient.contact_number,
        'consultant_name': patient.consultant.name,
        'consultant_id': patient.consultant_id
    })

@app.route('/register_returning_patient', methods=['POST'])
def register_returning_patient():
    try:
        patient_id = request.form.get('patient_id')
        weight_kg = request.form.get('weight_kg')
        
        patient = Patient.query.get_or_404(patient_id)
        
        # Allow multiple visits per day - removed restriction
        
        # Create new visit
        visit = Visit(
            patient_id=patient.id,
            consultant_id=patient.consultant_id,
            weight_kg=float(weight_kg) if weight_kg else None
        )
        
        db.session.add(visit)
        db.session.commit()
        
        app.logger.info(f'Returning patient visit created: {patient.registration_number}')
        
        return redirect(url_for('receptionist', success=f'Patient {patient.full_name} added to today\'s queue'))
        
    except Exception as e:
        app.logger.error(f'Error registering returning patient: {e}')
        db.session.rollback()
        return redirect(url_for('receptionist', error='Error registering returning patient'))

@app.route('/register_patient', methods=['POST'])
def register_patient():
    """Register a new patient with enhanced data"""
    try:
        registration_number = generate_registration_number()
        
        patient = Patient(
            registration_number=registration_number,
            full_name=request.form['full_name'],
            parent_name=request.form.get('parent_name', ''),
            date_of_birth=datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date(),
            address=request.form['address'],
            contact_number=request.form['contact_number'],
            email=request.form.get('email', ''),
            gender=request.form['gender'],
            consultant_id=int(request.form['consultant_id'])
        )
        
        db.session.add(patient)
        db.session.commit()
        
        # Create a visit record for today with weight
        visit = Visit(
            patient_id=patient.id,
            consultant_id=patient.consultant_id,
            status='waiting',
            weight_kg=float(request.form['weight_kg']) if request.form.get('weight_kg') else None
        )
        db.session.add(visit)
        db.session.commit()
        
        flash(f'Patient registered successfully! Registration Number: {registration_number}', 'success')
        logging.info(f"New patient registered: {registration_number}")
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error registering patient: {str(e)}', 'error')
        logging.error(f"Error registering patient: {str(e)}")
    
    return redirect(url_for('receptionist'))




@app.route('/get_patient/<reg_number>')
def get_patient(reg_number):
    patient = Patient.query.filter_by(registration_number=reg_number).first()
    if patient:
        return jsonify({
            'full_name': patient.full_name,
            'parent_name': patient.parent_name,
            'date_of_birth': patient.date_of_birth.strftime('%Y-%m-%d'),
            'address': patient.address,
            'contact_number': patient.contact_number,
            'email': patient.email,
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
    selected_consultant = None
    greeting = ""
    
    if consultant_id:
        selected_consultant = Consultant.query.get(consultant_id)
        # Get today's visits for this consultant
        today = date.today()
        
        # Limit queues to fit page better - 8 waiting, 5 completed
        waiting_visits = Visit.query.join(Patient).filter(
            Visit.consultant_id == consultant_id,
            Visit.status == 'waiting',
            func.date(Visit.visit_date) == today
        ).order_by(Visit.visit_date.asc()).limit(8).all()
        
        # Show completed visits from today - they persist until shift ends
        # The completed queue should remain visible throughout the shift
        completed_visits = Visit.query.join(Patient).filter(
            Visit.consultant_id == consultant_id,
            Visit.status == 'completed',
            func.date(Visit.visit_date) == today
        ).order_by(Visit.completed_at.desc()).limit(5).all()
        
        # Generate time-based greeting
        from datetime import datetime
        import pytz
        
        # Sri Lankan timezone
        lk_tz = pytz.timezone('Asia/Colombo')
        current_time = datetime.now(lk_tz)
        hour = current_time.hour
        
        if 5 <= hour < 12:
            greeting = "Good Morning"
        elif 12 <= hour < 17:
            greeting = "Good Afternoon"
        else:
            greeting = "Good Evening"
    
    # Count totals for the day (not limited)
    total_waiting = 0
    total_completed = 0
    if consultant_id:
        today = date.today()
        total_waiting = Visit.query.filter(
            Visit.consultant_id == consultant_id,
            Visit.status == 'waiting',
            func.date(Visit.visit_date) == today
        ).count()
        
        # Count all completed visits for today - persists until shift ends
        total_completed = Visit.query.filter(
            Visit.consultant_id == consultant_id,
            Visit.status == 'completed',
            func.date(Visit.visit_date) == today
        ).count()
    
    return render_template('consultant_simple.html', 
                         consultants=consultants,
                         waiting_visits=waiting_visits,
                         completed_visits=completed_visits,
                         selected_consultant_id=consultant_id,
                         selected_consultant=selected_consultant,
                         greeting=greeting,
                         total_waiting=total_waiting,
                         total_completed=total_completed)

@app.route('/set_selected_patient', methods=['POST'])
def set_selected_patient():
    """Set the currently selected patient for consultant synchronization"""
    reg_number = request.form.get('registration_number')
    consultant_id = request.form.get('consultant_id')
    
    if reg_number and consultant_id:
        # Store in session for this consultant
        session[f'selected_patient_{consultant_id}'] = {
            'registration_number': reg_number,
            'timestamp': datetime.now().isoformat()
        }
        return jsonify({'success': True})
    return jsonify({'success': False}), 400

@app.route('/get_selected_patient/<int:consultant_id>')
def get_selected_patient(consultant_id):
    """Get the currently selected patient for a consultant"""
    selected = session.get(f'selected_patient_{consultant_id}')
    if selected:
        return jsonify(selected)
    return jsonify({'registration_number': None})

@app.route('/get_patient_details/<reg_number>')
def get_patient_details(reg_number):
    patient = Patient.query.filter_by(registration_number=reg_number).first()
    if patient:
        # Get recent visits with weight data
        recent_visits = Visit.query.filter_by(patient_id=patient.id)\
                                  .filter(Visit.status.in_(['completed', 'completed_archived']))\
                                  .order_by(Visit.visit_date.desc())\
                                  .limit(5).all()
        
        visit_data = []
        for visit in recent_visits:
            visit_info = {
                'date': visit.visit_date.strftime('%Y-%m-%d'),
                'weight': f"{visit.weight_kg} kg" if visit.weight_kg else None
            }
            visit_data.append(visit_info)
        
        # Get most recent visit weight if any
        current_visit = Visit.query.filter_by(patient_id=patient.id)\
                                  .filter(Visit.status.in_(['waiting', 'completed']))\
                                  .order_by(Visit.visit_date.desc())\
                                  .first()
        
        current_weight = current_visit.weight_kg if current_visit and current_visit.weight_kg else None
        
        return jsonify({
            'registration_number': patient.registration_number,
            'full_name': patient.full_name,
            'parent_name': patient.parent_name,
            'age': patient.age,  # Just the age number
            'gender': patient.gender,
            'date_of_birth': patient.date_of_birth.strftime('%Y-%m-%d'),
            'email': patient.email,
            'weight_kg': current_weight,
            'consultant_id': patient.consultant_id,
            'recent_visits': visit_data
        })
    return jsonify({'error': 'Patient not found'}), 404

@app.route('/mark_complete', methods=['POST'])
def mark_complete():
    """Mark consultation as complete"""
    reg_number = request.form['registration_number']
    patient = Patient.query.filter_by(registration_number=reg_number).first()
    
    if not patient:
        return jsonify({'success': False, 'error': 'Patient not found'}), 404
    
    # Find the most recent waiting visit for this patient (allow multiple visits per day)
    visit = Visit.query.filter(
        Visit.patient_id == patient.id,
        Visit.status == 'waiting'
    ).order_by(Visit.visit_date.desc()).first()
    
    if not visit:
        return jsonify({'success': False, 'error': 'No active visit found for this patient'}), 400
    
    # Mark consultation as complete
    visit.mark_completed()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Consultation completed for {patient.full_name}'
    })

@app.route('/clear_consultant_selection', methods=['POST'])
def clear_consultant_selection():
    """Clear all consultant selections"""
    # Clear all consultant selections from session
    keys_to_remove = [key for key in session.keys() if key.startswith('selected_patient_')]
    for key in keys_to_remove:
        session.pop(key, None)
    return jsonify({'success': True})



@app.route('/complete_consultation', methods=['POST'])
def complete_consultation():
    reg_number = request.form['registration_number']
    patient = Patient.query.filter_by(registration_number=reg_number).first()
    
    if patient:
        # Find the most recent waiting visit for this patient
        visit = Visit.query.filter(
            Visit.patient_id == patient.id,
            Visit.status == 'waiting'
        ).order_by(Visit.visit_date.desc()).first()
        
        if visit:
            consultant_id = visit.consultant_id
            visit.mark_completed()
            
            # Find the next patient in line for the same consultant
            next_visit = Visit.query.join(Patient).filter(
                Visit.consultant_id == consultant_id,
                Visit.status == 'waiting',
                func.date(Visit.visit_date) == today
            ).order_by(Visit.visit_date.asc()).first()
            
            next_patient_data = None
            if next_visit:
                next_patient_data = {
                    'registration_number': next_visit.patient.registration_number,
                    'full_name': next_visit.patient.full_name
                }
            
            return jsonify({
                'success': True,
                'message': f'Consultation completed for {patient.full_name}',
                'next_patient': next_patient_data
            })
        else:
            return jsonify({'success': False, 'error': 'No active visit found for this patient'}), 400
    else:
        return jsonify({'success': False, 'error': 'Patient not found'}), 404

@app.route('/report', methods=['GET', 'POST'])
def report():
    consultants = Consultant.query.all()
    report_data = None
    
    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        consultant_id = request.form.get('consultant_id')
        
        # Build query for completed visits within date range (excluding incomplete consultations)
        query = Visit.query.join(Patient).filter(
            Visit.status.in_(['completed', 'completed_archived']),  # Only completed visits in summary count
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
        Visit.status.in_(['completed', 'completed_archived']),
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

@app.route('/reset_daily_queue', methods=['POST'])
def reset_daily_queue():
    """Reset all visits for today (dangerous operation)"""
    try:
        today = date.today()
        
        # Delete all visits for today
        visits_deleted = Visit.query.filter(
            func.date(Visit.visit_date) == today
        ).delete()
        
        db.session.commit()
        
        app.logger.warning(f'Daily queue reset: {visits_deleted} visits deleted for {today}')
        
        return jsonify({
            'success': True,
            'message': f'Queue reset successfully. {visits_deleted} visits removed.',
            'visits_deleted': visits_deleted
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error resetting daily queue: {e}')
        return jsonify({
            'success': False,
            'error': f'Error resetting queue: {str(e)}'
        }), 500

@app.route('/print_daily_summary')
def print_daily_summary():
    """Print summary of all consultations for a specific date"""
    date_str = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    
    try:
        report_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Get all visits for the date
        visits = Visit.query.join(Patient).join(Consultant).filter(
            func.date(Visit.visit_date) == report_date
        ).order_by(Visit.visit_date.asc()).all()
        
        # Count statistics
        total_visits = len(visits)
        waiting_count = len([v for v in visits if v.status == 'waiting'])
        completed_count = len([v for v in visits if v.status == 'completed'])
        
        # Group by consultant
        consultant_stats = {}
        for visit in visits:
            consultant_name = visit.consultant.name
            if consultant_name not in consultant_stats:
                consultant_stats[consultant_name] = {
                    'waiting': 0,
                    'completed': 0,
                    'total': 0
                }
            consultant_stats[consultant_name][visit.status] += 1
            consultant_stats[consultant_name]['total'] += 1
        
        return render_template('print_daily_summary.html',
                             visits=visits,
                             report_date=report_date,
                             total_visits=total_visits,
                             waiting_count=waiting_count,
                             completed_count=completed_count,
                             consultant_stats=consultant_stats)
        
    except Exception as e:
        app.logger.error(f'Error generating daily summary: {e}')
        flash(f'Error generating report: {str(e)}', 'error')
        return redirect(url_for('queue_management'))

@app.route('/print_patient/<reg_number>')
def print_patient(reg_number):
    """Print individual patient summary"""
    patient = Patient.query.filter_by(registration_number=reg_number).first()
    
    if not patient:
        flash('Patient not found', 'error')
        return redirect(url_for('queue_management'))
    
    # Get today's visit
    today = date.today()
    current_visit = Visit.query.filter_by(patient_id=patient.id)\
                              .filter(func.date(Visit.visit_date) == today)\
                              .first()
    
    # Get recent visits for history
    recent_visits = Visit.query.filter_by(patient_id=patient.id)\
                              .filter(Visit.status.in_(['completed', 'completed_archived']))\
                              .order_by(Visit.visit_date.desc())\
                              .limit(5).all()
    
    return render_template('print_patient.html',
                         patient=patient,
                         current_visit=current_visit,
                         recent_visits=recent_visits,
                         print_date=date.today())

# Admin Panel Routes
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'drajitha' and password == 'ajith@galle':
            session['admin_logged_in'] = True
            flash('Admin login successful', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin_panel')
def admin_panel():
    if not session.get('admin_logged_in'):
        flash('Please log in to access admin panel', 'error')
        return redirect(url_for('admin_login'))
    
    consultants = Consultant.query.all()
    total_patients = Patient.query.count()
    total_visits = Visit.query.count()
    
    return render_template('admin_panel.html', 
                         consultants=consultants,
                         total_patients=total_patients,
                         total_visits=total_visits)

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('report'))

@app.route('/admin/add_consultant', methods=['POST'])
def admin_add_consultant():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    name = request.form.get('name', '').strip()
    consultation_fee = request.form.get('consultation_fee', 0.0, type=float)
    
    if not name:
        flash('Consultant name is required', 'error')
        return redirect(url_for('admin_panel'))
    
    # Check if consultant already exists
    existing = Consultant.query.filter_by(name=name).first()
    if existing:
        flash('Consultant with this name already exists', 'error')
        return redirect(url_for('admin_panel'))
    
    try:
        consultant = Consultant(name=name, consultation_fee=consultation_fee)
        db.session.add(consultant)
        db.session.commit()
        flash(f'Consultant "{name}" added successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding consultant: {str(e)}', 'error')
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/edit_consultant', methods=['POST'])
def admin_edit_consultant():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    consultant_id = request.form.get('consultant_id')
    new_name = request.form.get('name', '').strip()
    consultation_fee = request.form.get('consultation_fee', 0.0, type=float)
    
    if not new_name:
        flash('Consultant name is required', 'error')
        return redirect(url_for('admin_panel'))
    
    consultant = Consultant.query.get_or_404(consultant_id)
    
    # Check if new name already exists (excluding current consultant)
    existing = Consultant.query.filter(
        Consultant.name == new_name,
        Consultant.id != consultant_id
    ).first()
    
    if existing:
        flash('Another consultant with this name already exists', 'error')
        return redirect(url_for('admin_panel'))
    
    try:
        old_name = consultant.name
        consultant.name = new_name
        consultant.consultation_fee = consultation_fee
        db.session.commit()
        flash(f'Consultant "{old_name}" updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating consultant: {str(e)}', 'error')
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/cleanup_data', methods=['POST'])
def admin_cleanup_data():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    cleanup_type = request.form.get('cleanup_type')
    
    if cleanup_type == 'date_range':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        if not start_date or not end_date:
            flash('Please select both start and end dates', 'error')
            return redirect(url_for('admin_panel'))
        
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if start_date > end_date:
            flash('Start date must be before end date', 'error')
            return redirect(url_for('admin_panel'))
        
        try:
            # Delete visits within the specified date range
            visits_to_delete = Visit.query.filter(
                func.date(Visit.visit_date) >= start_date,
                func.date(Visit.visit_date) <= end_date
            ).all()
            visit_count = len(visits_to_delete)
            
            for visit in visits_to_delete:
                db.session.delete(visit)
            
            # Find patients with no remaining visits and delete them
            patients_with_no_visits = Patient.query.filter(
                ~Patient.id.in_(db.session.query(Visit.patient_id))
            ).all()
            
            patient_count = len(patients_with_no_visits)
            
            for patient in patients_with_no_visits:
                db.session.delete(patient)
            
            db.session.commit()
            
            flash(f'Date range cleanup completed: {visit_count} visits and {patient_count} patients deleted between {start_date} and {end_date}', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error during date range cleanup: {str(e)}', 'error')
    
    elif cleanup_type == 'selected_visits':
        visit_ids = request.form.getlist('visit_ids')
        delete_patient = request.form.get('delete_patient') == 'on'
        
        if not visit_ids:
            flash('Please select at least one visit to delete', 'error')
            return redirect(url_for('admin_panel'))
        
        try:
            # Get visits to delete
            visits_to_delete = Visit.query.filter(Visit.id.in_(visit_ids)).all()
            patient = visits_to_delete[0].patient if visits_to_delete else None
            
            # Delete selected visits
            for visit in visits_to_delete:
                db.session.delete(visit)
            
            deleted_count = len(visits_to_delete)
            
            # Delete patient if requested and no other visits remain
            patient_deleted = False
            if delete_patient and patient:
                remaining_visits = Visit.query.filter_by(patient_id=patient.id).filter(~Visit.id.in_(visit_ids)).count()
                if remaining_visits == 0:
                    db.session.delete(patient)
                    patient_deleted = True
            
            db.session.commit()
            
            message = f'{deleted_count} visit(s) deleted successfully'
            if patient_deleted:
                message += f' and patient "{patient.full_name}" removed'
            
            flash(message, 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting visits: {str(e)}', 'error')
    
    elif cleanup_type == 'before_date':
        cleanup_date = request.form.get('cleanup_date')
        if not cleanup_date:
            flash('Please select a cleanup date', 'error')
            return redirect(url_for('admin_panel'))
        
        cleanup_date = datetime.strptime(cleanup_date, '%Y-%m-%d').date()
        
        try:
            # Delete visits before the specified date
            visits_to_delete = Visit.query.filter(func.date(Visit.visit_date) < cleanup_date).all()
            visit_count = len(visits_to_delete)
            
            for visit in visits_to_delete:
                db.session.delete(visit)
            
            # Find patients with no remaining visits and delete them
            patients_with_no_visits = Patient.query.filter(
                ~Patient.id.in_(db.session.query(Visit.patient_id))
            ).all()
            
            patient_count = len(patients_with_no_visits)
            
            for patient in patients_with_no_visits:
                db.session.delete(patient)
            
            db.session.commit()
            
            flash(f'Data cleanup completed: {visit_count} visits and {patient_count} patients deleted before {cleanup_date}', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error during data cleanup: {str(e)}', 'error')
    
    else:
        flash('Invalid cleanup type selected', 'error')
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_consultant', methods=['POST'])
def admin_delete_consultant():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    consultant_id = request.form.get('consultant_id')
    
    try:
        consultant = Consultant.query.get_or_404(consultant_id)
        consultant_name = consultant.name
        
        # Check if consultant has any patients or visits
        patient_count = Patient.query.filter_by(consultant_id=consultant_id).count()
        visit_count = Visit.query.filter_by(consultant_id=consultant_id).count()
        
        if patient_count > 0 or visit_count > 0:
            flash(f'Cannot delete consultant "{consultant_name}": {patient_count} patients and {visit_count} visits are assigned to this consultant', 'error')
            return redirect(url_for('admin_panel'))
        
        # Safe to delete - no dependencies
        db.session.delete(consultant)
        db.session.commit()
        
        flash(f'Consultant "{consultant_name}" deleted successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting consultant: {str(e)}', 'error')
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/search_patient_visits')
def admin_search_patient_visits():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    reg_number = request.args.get('reg_number', '').strip()
    if not reg_number:
        return jsonify({'error': 'Registration number is required'}), 400
    
    patient = Patient.query.filter_by(registration_number=reg_number).first()
    if not patient:
        return jsonify({'error': f'Patient with registration number "{reg_number}" not found'}), 404
    
    visits = Visit.query.filter_by(patient_id=patient.id).order_by(Visit.visit_date.desc()).all()
    
    visit_data = []
    for visit in visits:
        visit_data.append({
            'id': visit.id,
            'visit_date': visit.visit_date.strftime('%Y-%m-%d'),
            'visit_time': visit.visit_date.strftime('%H:%M'),
            'status': visit.status,
            'consultant': visit.consultant.name,
            'completed_at': visit.completed_at.strftime('%H:%M') if visit.completed_at else None
        })
    
    return jsonify({
        'patient': {
            'registration_number': patient.registration_number,
            'full_name': patient.full_name,
            'date_of_birth': patient.date_of_birth.strftime('%Y-%m-%d'),
            'contact_number': patient.contact_number
        },
        'visits': visit_data
    })

@app.route('/end_shift', methods=['POST'])
def end_shift():
    """End shift for all consultants - clear waiting queue and archive completed visits"""
    try:
        today = date.today()
        
        # Get all waiting visits for today (all consultants)
        waiting_visits = Visit.query.filter(
            Visit.status == 'waiting',
            func.date(Visit.visit_date) == today
        ).all()
        
        # Get all completed visits for today to archive
        completed_visits = Visit.query.filter(
            Visit.status == 'completed',
            func.date(Visit.visit_date) == today
        ).all()
        
        # Delete waiting visits (non-completed consultations)
        for visit in waiting_visits:
            db.session.delete(visit)
        
        # Archive completed visits
        for visit in completed_visits:
            visit.status = 'completed_archived'
        
        # Clear all consultant selections
        keys_to_remove = [key for key in session.keys() if key.startswith('selected_patient_')]
        for key in keys_to_remove:
            session.pop(key, None)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Shift ended successfully. {len(waiting_visits)} waiting consultations cleared, {len(completed_visits)} completed consultations archived.'
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error ending shift: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500
