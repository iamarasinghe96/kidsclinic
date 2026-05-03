from flask import render_template, request, redirect, url_for, flash, jsonify, make_response, session
from datetime import datetime, date, timedelta
from sqlalchemy import or_, func, text
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

    # Get all consultants for dropdown
    consultants = Consultant.query.all()

    # Selected consultant filter — default to Dr. Ajith if no param given
    selected_consultant_id = request.args.get('consultant_id', type=int)
    if selected_consultant_id is None:
        ajith = Consultant.query.filter(Consultant.name.ilike('%ajith%')).first()
        if ajith:
            selected_consultant_id = ajith.id

    selected_consultant = Consultant.query.get(selected_consultant_id) if selected_consultant_id else None

    # Base queries for today
    waiting_q = Visit.query.join(Patient).join(Consultant).filter(
        Visit.status == 'waiting',
        func.date(Visit.visit_date) == today
    )
    completed_q = Visit.query.join(Patient).join(Consultant).filter(
        Visit.status == 'completed',
        func.date(Visit.visit_date) == today
    )

    # Apply consultant filter
    if selected_consultant_id:
        waiting_q = waiting_q.filter(Visit.consultant_id == selected_consultant_id)
        completed_q = completed_q.filter(Visit.consultant_id == selected_consultant_id)

    waiting_visits = waiting_q.order_by(Visit.visit_date.asc()).all()
    completed_visits = completed_q.order_by(Visit.completed_at.desc()).all()

    total_waiting = len(waiting_visits)
    total_completed = len(completed_visits)
    total_patients_today = total_waiting + total_completed

    return render_template('queue_management.html',
                         waiting_visits=waiting_visits,
                         completed_visits=completed_visits,
                         consultants=consultants,
                         selected_consultant_id=selected_consultant_id,
                         selected_consultant=selected_consultant,
                         total_waiting=total_waiting,
                         total_completed=total_completed,
                         total_patients_today=total_patients_today)

@app.route('/api/queue_status')
def api_queue_status():
    """API endpoint to check current queue status without full page load"""
    today = date.today()
    consultant_id = request.args.get('consultant_id', type=int)

    waiting_q = Visit.query.join(Patient).filter(
        Visit.status == 'waiting',
        func.date(Visit.visit_date) == today
    )
    completed_q = Visit.query.join(Patient).filter(
        Visit.status == 'completed',
        func.date(Visit.visit_date) == today
    )

    if consultant_id:
        waiting_q = waiting_q.filter(Visit.consultant_id == consultant_id)
        completed_q = completed_q.filter(Visit.consultant_id == consultant_id)

    waiting_count = waiting_q.count()
    completed_count = completed_q.count()

    return jsonify({
        'waiting_count': waiting_count,
        'completed_count': completed_count,
        'total_count': waiting_count + completed_count,
        'timestamp': datetime.now().isoformat()
    })

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
                    date_of_birth=datetime.strptime(request.form['date_of_birth'], '%d/%m/%Y').date(),
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
            'title': getattr(patient, 'title', ''),
            'full_name': patient.full_name,
            'registration_number': patient.registration_number,
            'date_of_birth': patient.date_of_birth.strftime('%d/%m/%Y'),
            'contact_number': patient.contact_number,
            'consultant_name': patient.consultant.name,
            'consultant': patient.consultant.name,
            'consultant_id': patient.consultant_id
        })
    
    return jsonify(results)

@app.route('/get_patient_details_by_id/<int:patient_id>')
def get_patient_details_by_id(patient_id):
    """Get patient details by ID for editing"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        
        return jsonify({
            'id': patient.id,
            'title': getattr(patient, 'title', ''),
            'full_name': patient.full_name,
            'registration_number': patient.registration_number,
            'parent_name': getattr(patient, 'parent_name', ''),
            'date_of_birth_formatted': patient.date_of_birth.strftime('%d/%m/%Y'),
            'address': patient.address,
            'contact_number': patient.contact_number,
            'email': getattr(patient, 'email', ''),
            'gender': patient.gender,
            'consultant_id': patient.consultant_id
        })
        
    except Exception as e:
        logging.error(f"Error getting patient details for ID {patient_id}: {e}")
        return jsonify({'error': str(e)})

@app.route('/register_returning_patient', methods=['POST'])
def register_returning_patient():
    try:
        # Get form data
        registration_number = request.form.get('registration_number')
        title = request.form.get('title', '')
        full_name = request.form.get('full_name')
        consultant_id = request.form.get('consultant_id')
        weight_kg = request.form.get('weight_kg')
        
        # Find patient by registration number
        patient = Patient.query.filter_by(registration_number=registration_number).first()
        
        if not patient:
            flash('Patient not found with this registration number.', 'error')
            return redirect(url_for('receptionist'))
        
        # Update patient details if provided
        if title and hasattr(patient, 'title'):
            patient.title = title
        if full_name:
            patient.full_name = full_name
        if consultant_id:
            patient.consultant_id = int(consultant_id)
        
        # Create new visit
        visit = Visit(
            patient_id=patient.id,
            consultant_id=patient.consultant_id,
            weight_kg=float(weight_kg) if weight_kg else None
        )
        
        db.session.add(visit)
        db.session.commit()
        
        app.logger.info(f'Returning patient visit created: {patient.registration_number}')
        
        flash(f'Welcome back, {patient.full_name}! Visit registered.', 'success')
        return redirect(url_for('receptionist'))
        
    except Exception as e:
        app.logger.error(f'Error registering returning patient: {e}')
        db.session.rollback()
        flash('Error registering returning patient', 'error')
        return redirect(url_for('receptionist'))

@app.route('/register_patient', methods=['POST'])
def register_patient():
    """Register a new patient with enhanced data"""
    try:
        registration_number = generate_registration_number()
        
        patient = Patient(
            registration_number=registration_number,
            title=request.form.get('title', ''),
            full_name=request.form['full_name'],
            parent_name=request.form.get('parent_name', ''),
            date_of_birth=datetime.strptime(request.form['date_of_birth'], '%d/%m/%Y').date(),
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
        app.logger.info(f"New patient registered: {registration_number}")
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error registering patient: {str(e)}', 'error')
        app.logger.error(f"Error registering patient: {str(e)}")
    
    return redirect(url_for('receptionist'))




@app.route('/get_patient/<reg_number>')
def get_patient(reg_number):
    patient = Patient.query.filter_by(registration_number=reg_number).first()
    if patient:
        return jsonify({
            'title': patient.title or '',
            'full_name': patient.display_name,
            'parent_name': patient.parent_name,
            'date_of_birth': patient.date_of_birth.strftime('%d/%m/%Y'),
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
    """Set currently selected patient (called by receptionist)"""
    consultant_id = request.json.get('consultant_id')
    registration_number = request.json.get('registration_number')
    
    if not hasattr(app, 'selected_patients'):
        app.selected_patients = {}
    
    if registration_number:
        app.selected_patients[consultant_id] = registration_number
        logging.info(f"Selected patient {registration_number} for consultant {consultant_id}")
    else:
        # Clear selection
        app.selected_patients.pop(consultant_id, None)
        logging.info(f"Cleared patient selection for consultant {consultant_id}")
    
    return jsonify({'success': True})

@app.route('/get_selected_patient/<int:consultant_id>')
def get_selected_patient(consultant_id):
    """Get currently selected patient by receptionist for this consultant"""
    # Use global variable to track selected patient
    if not hasattr(app, 'selected_patients'):
        app.selected_patients = {}
    
    selected_reg = app.selected_patients.get(consultant_id)
    
    if selected_reg:
        return jsonify({'registration_number': selected_reg})
    else:
        return jsonify({'registration_number': None})

@app.route('/get_patient_details/<reg_number>')
def get_patient_details(reg_number):
    try:
        patient = Patient.query.filter_by(registration_number=reg_number).first()
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404

        recent_visits = Visit.query.filter_by(patient_id=patient.id)\
                                  .filter(Visit.status.in_(['completed', 'completed_archived']))\
                                  .order_by(Visit.visit_date.desc()).all()

        total_visits = Visit.query.filter_by(patient_id=patient.id).count()

        visit_data = []
        for visit in recent_visits:
            visit_data.append({
                'date': visit.visit_date.strftime('%d/%m/%Y'),
                'weight': f"{visit.weight_kg} kg" if visit.weight_kg else None
            })

        current_visit = Visit.query.filter_by(patient_id=patient.id)\
                                  .filter(Visit.status.in_(['waiting', 'completed']))\
                                  .order_by(Visit.visit_date.desc())\
                                  .first()

        current_weight = current_visit.weight_kg if current_visit and current_visit.weight_kg else None

        age = patient.age
        gender = patient.gender
        if age <= 5:
            calc_title = 'Baby'
        elif age <= 17:
            calc_title = 'Master' if gender == 'Male' else 'Miss'
        else:
            calc_title = 'Adult Male' if gender == 'Male' else 'Adult Female'

        return jsonify({
            'registration_number': patient.registration_number,
            'full_name': patient.full_name,
            'parent_name': patient.parent_name,
            'age': patient.age,
            'gender': patient.gender,
            'date_of_birth': patient.date_of_birth.strftime('%d/%m/%Y'),
            'email': patient.email,
            'total_visits': total_visits,
            'calc_title': calc_title,
            'weight_kg': current_weight,
            'consultant_id': patient.consultant_id,
            'recent_visits': visit_data
        })
    except Exception as e:
        logging.exception('get_patient_details failed for %s', reg_number)
        return jsonify({'error': str(e)}), 500

@app.route('/get_queue_state/<int:consultant_id>')
def get_queue_state(consultant_id):
    """Return current waiting and completed lists for live queue diffing."""
    today = date.today()
    waiting = Visit.query.filter(
        Visit.consultant_id == consultant_id,
        Visit.status == 'waiting',
        func.date(Visit.visit_date) == today
    ).order_by(Visit.visit_date.asc()).all()

    completed = Visit.query.filter(
        Visit.consultant_id == consultant_id,
        Visit.status == 'completed',
        func.date(Visit.visit_date) == today
    ).order_by(Visit.completed_at.desc()).all()

    _title_colors = {
        'Baby': '#fd7e14', 'Master': '#0d6efd', 'Miss': '#d63384',
        'Adult Male': '#198754', 'Adult Female': '#6f42c1'
    }

    def _badge(p):
        age, gender = p.age, p.gender
        if age <= 5:
            t = 'Baby'
        elif age <= 17:
            t = 'Master' if gender == 'Male' else 'Miss'
        else:
            t = 'Adult Male' if gender == 'Male' else 'Adult Female'
        return t, _title_colors.get(t, '#6c757d')

    return jsonify({
        'waiting': [{
            'reg':        v.patient.registration_number,
            'name':       v.patient.full_name,
            'time':       v.visit_date.strftime('%H:%M'),
            'weight':     v.weight_kg,
            'calcTitle':  _badge(v.patient)[0],
            'titleColor': _badge(v.patient)[1],
        } for v in waiting],
        'completed': [{
            'reg':  v.patient.registration_number,
            'name': v.patient.display_name,
            'time': v.completed_at.strftime('%H:%M') if v.completed_at else ''
        } for v in completed]
    })

@app.route('/get_patient_info_html/<reg_number>')
def get_patient_info_html(reg_number):
    """Return server-rendered HTML for the patient info panel."""
    from flask import render_template_string
    try:
        patient = Patient.query.filter_by(registration_number=reg_number).first()
        if not patient:
            return '<p class="text-danger">Patient not found</p>', 404

        recent_visits = Visit.query.filter_by(patient_id=patient.id)\
                                   .filter(Visit.status.in_(['completed', 'completed_archived']))\
                                   .order_by(Visit.visit_date.desc()).all()
        total_visits = Visit.query.filter_by(patient_id=patient.id).count()

        current_visit = Visit.query.filter_by(patient_id=patient.id)\
                                   .filter(Visit.status.in_(['waiting', 'completed']))\
                                   .order_by(Visit.visit_date.desc()).first()
        weight_kg = current_visit.weight_kg if current_visit and current_visit.weight_kg else None

        age = patient.age
        gender = patient.gender
        if age <= 5:
            calc_title = 'Baby'
        elif age <= 17:
            calc_title = 'Master' if gender == 'Male' else 'Miss'
        else:
            calc_title = 'Adult Male' if gender == 'Male' else 'Adult Female'

        title_colors = {
            'Baby': '#fd7e14', 'Master': '#0d6efd', 'Miss': '#d63384',
            'Adult Male': '#198754', 'Adult Female': '#6f42c1'
        }
        title_color = title_colors.get(calc_title, '#6c757d')

        tmpl = """
<div class="patient-details">
  <div class="d-flex align-items-center gap-2 mb-3">
    <span class="fw-bold fs-6">{{ patient.full_name }}</span>
    <span style="background:{{ title_color }};color:white;border-radius:10px;padding:2px 10px;font-size:0.78rem;white-space:nowrap;">{{ calc_title }}</span>
  </div>
  <div class="info-row mb-2"><span class="fw-bold">Registration #:</span><span class="ms-2">{{ patient.registration_number }}</span></div>
  <div class="info-row mb-2"><span class="fw-bold">Age:</span><span class="ms-2">{{ patient.age }} years</span></div>
  <div class="info-row mb-2"><span class="fw-bold">Gender:</span><span class="ms-2">{{ patient.gender }}{% if weight_kg %} &nbsp;·&nbsp; {{ weight_kg }} kg{% endif %}</span></div>
  <div class="info-row mb-2"><span class="fw-bold">Date of Birth:</span><span class="ms-2">{{ patient.date_of_birth.strftime('%d/%m/%Y') }}</span></div>
  {% if patient.parent_name %}<div class="info-row mb-2"><span class="fw-bold">Parent:</span><span class="ms-2">{{ patient.parent_name }}</span></div>{% endif %}
  {% if patient.email %}<div class="info-row mb-2"><span class="fw-bold">Email:</span><span class="ms-2">{{ patient.email }}</span></div>{% endif %}
  <div class="mt-3">
    <h6>Recent Visits: <span class="badge bg-secondary">{{ total_visits }} visit{{ 's' if total_visits != 1 else '' }}</span></h6>
    <div class="visits-scroll-wrapper">
      <div class="visits-scroll">
        {% for v in recent_visits %}
          <span class="visit-chip">{{ v.visit_date.strftime('%d/%m/%Y') }}{% if v.weight_kg %} &middot; {{ v.weight_kg }} kg{% endif %}</span>
        {% else %}
          <span class="text-muted small">No previous visits</span>
        {% endfor %}
      </div>
    </div>
  </div>
</div>
"""
        html = render_template_string(tmpl,
            patient=patient,
            recent_visits=recent_visits,
            total_visits=total_visits,
            weight_kg=weight_kg,
            calc_title=calc_title,
            title_color=title_color)
        return html
    except Exception as e:
        logging.exception('get_patient_info_html failed for %s', reg_number)
        return f'<p class="text-danger">Error loading patient information: {e}</p>', 500

@app.route('/mark_complete', methods=['POST'])
def mark_complete():
    """Mark consultation as complete"""
    reg_number = request.form['registration_number']
    redirect_url = request.form.get('redirect_url')
    patient = Patient.query.filter_by(registration_number=reg_number).first()

    if not patient:
        if redirect_url:
            return redirect(redirect_url)
        return jsonify({'success': False, 'error': 'Patient not found'}), 404

    # Find the most recent waiting visit for this patient (allow multiple visits per day)
    visit = Visit.query.filter(
        Visit.patient_id == patient.id,
        Visit.status == 'waiting'
    ).order_by(Visit.visit_date.desc()).first()

    if not visit:
        if redirect_url:
            return redirect(redirect_url)
        return jsonify({'success': False, 'error': 'No active visit found for this patient'}), 400

    # Mark consultation as complete
    visit.mark_completed()
    db.session.commit()

    if redirect_url:
        return redirect(redirect_url)
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
    
    if not patient:
        return jsonify({'success': False, 'error': 'Patient not found'}), 404
    
    # Find the most recent waiting visit for this patient
    visit = Visit.query.filter(
        Visit.patient_id == patient.id,
        Visit.status == 'waiting'
    ).order_by(Visit.visit_date.desc()).first()
    
    if not visit:
        return jsonify({'success': False, 'error': 'No active visit found'}), 400
    
    # Mark consultation as complete
    visit.mark_completed()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Consultation completed for {patient.full_name}'
    })

@app.route('/send_emergency_message', methods=['POST'])
def send_emergency_message():
    """Send emergency message to consultant displays"""
    message = request.form.get('message', '').strip()
    
    if not message:
        return jsonify({'success': False, 'error': 'Message is required'}), 400
    
    # Store the emergency message globally so all consultants can see it
    timestamp = datetime.now().strftime('%H:%M:%S')
    emergency_data = {
        'message': message,
        'timestamp': timestamp,
        'expires_at': (datetime.now() + timedelta(seconds=15)).isoformat()  # 15 seconds display
    }
    
    # Store globally instead of in session
    app.emergency_message_data = emergency_data
    logging.info(f"Emergency message sent: {message}")
    
    return jsonify({
        'success': True,
        'message': 'Emergency message sent to all consultants'
    })

@app.route('/get_emergency_message', methods=['GET'])
def get_emergency_message():
    """Get current emergency message for consultant displays"""
    # Use global variable instead of session to ensure all consultants see it
    global emergency_message_data
    
    if not hasattr(app, 'emergency_message_data'):
        app.emergency_message_data = None
    
    if not app.emergency_message_data:
        return jsonify({'message': None})
    
    # Check if message has expired (15 seconds)
    try:
        expires_at = datetime.fromisoformat(app.emergency_message_data['expires_at'])
        if datetime.now() > expires_at:
            # Message expired, clear it
            app.emergency_message_data = None
            return jsonify({'message': None})
    except:
        # Invalid timestamp, clear message
        app.emergency_message_data = None
        return jsonify({'message': None})
    
    return jsonify({
        'message': app.emergency_message_data['message'],
        'timestamp': app.emergency_message_data['timestamp']
    })



@app.route('/clear_emergency_message', methods=['POST'])
def clear_emergency_message():
    """Clear emergency message"""
    session.pop('emergency_message', None)
    return jsonify({'success': True})

@app.route('/report', methods=['GET', 'POST'])
def report():
    consultants = Consultant.query.all()
    report_data = None
    
    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        consultant_id = request.form.get('consultant_id')
        
        # Build query for visits within date range (include all relevant statuses)
        query = Visit.query.join(Patient).filter(
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
    
    # Build query for all visits within date range
    query = Visit.query.join(Patient).filter(
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

@app.route('/delete_visit/<int:visit_id>', methods=['POST'])
def delete_visit(visit_id):
    """Delete a specific visit from the queue"""
    try:
        # Find the visit
        visit = Visit.query.get(visit_id)
        if not visit:
            return jsonify({
                'success': False,
                'error': 'Visit not found'
            }), 404
        
        patient_name = visit.patient.display_name
        visit_date = visit.visit_date.strftime('%Y-%m-%d %H:%M')
        
        # Delete only this visit, not the patient
        db.session.delete(visit)
        db.session.commit()
        
        app.logger.info(f'Visit deleted from queue: {patient_name} - {visit_date} (ID: {visit_id})')
        
        return jsonify({
            'success': True,
            'message': f'Visit for {patient_name} removed from queue'
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error deleting visit {visit_id}: {e}')
        return jsonify({
            'success': False,
            'error': f'Error removing visit: {str(e)}'
        }), 500

@app.route('/delete_patient/<int:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    """Delete a patient and all associated visits"""
    try:
        # Find the patient
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({
                'success': False,
                'error': 'Patient not found'
            }), 404
        
        patient_name = patient.display_name
        
        # Delete all visits associated with this patient first
        visits_deleted = Visit.query.filter_by(patient_id=patient_id).delete()
        
        # Delete the patient
        db.session.delete(patient)
        db.session.commit()
        
        app.logger.info(f'Patient deleted: {patient_name} (ID: {patient_id}), {visits_deleted} visits removed')
        
        return jsonify({
            'success': True,
            'message': f'Patient {patient_name} deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error deleting patient {patient_id}: {e}')
        return jsonify({
            'success': False,
            'error': f'Error deleting patient: {str(e)}'
        }), 500

@app.route('/admin_panel')
def admin_panel():
    """Admin panel for managing consultants and patient data"""
    try:
        consultants = Consultant.query.all()
        # Handle missing color attribute gracefully
        for consultant in consultants:
            if not hasattr(consultant, 'color') or getattr(consultant, 'color', None) is None:
                consultant.color = '#6c757d'  # Default color
    except Exception as e:
        app.logger.error(f"Error accessing consultants: {e}")
        consultants = []
    return render_template('admin_panel.html', consultants=consultants)

@app.route('/admin/add_consultant', methods=['POST'])
def add_consultant():
    """Add a new consultant"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        color = data.get('color', '#6c757d')
        
        if not name:
            return jsonify({'success': False, 'error': 'Consultant name is required'})
        
        # Check if consultant already exists
        existing = Consultant.query.filter_by(name=name).first()
        if existing:
            return jsonify({'success': False, 'error': 'Consultant with this name already exists'})
        
        # Try to create consultant with color, fallback if color field doesn't exist
        try:
            consultant = Consultant(name=name, color=color)
        except TypeError:
            # Color field might not exist yet, create without it
            consultant = Consultant(name=name)
            
        db.session.add(consultant)
        db.session.commit()
        
        # Add color using raw SQL if the model doesn't support it
        if not hasattr(consultant, 'color'):
            try:
                db.session.execute(
                    text('UPDATE consultant SET color = :color WHERE id = :id'),
                    {'color': color, 'id': consultant.id}
                )
                db.session.commit()
            except Exception:
                pass  # Ignore if color column doesn't exist
        
        app.logger.info(f'New consultant added: {name}')
        
        return jsonify({'success': True, 'message': f'Consultant {name} added successfully'})
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error adding consultant: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/delete_consultant/<int:consultant_id>', methods=['POST'])
def delete_consultant(consultant_id):
    """Delete a consultant and all associated visits and patients"""
    try:
        consultant = Consultant.query.get(consultant_id)
        if not consultant:
            return jsonify({'success': False, 'error': 'Consultant not found'})
        
        consultant_name = consultant.name
        
        # Get all patients assigned to this consultant
        patients = Patient.query.filter_by(consultant_id=consultant_id).all()
        patients_deleted = len(patients)
        
        # Delete all visits for this consultant first
        visits_deleted = Visit.query.filter_by(consultant_id=consultant_id).delete()
        
        # Delete all patients assigned to this consultant (this will also cascade delete their visits)
        Patient.query.filter_by(consultant_id=consultant_id).delete()
        
        # Delete the consultant
        db.session.delete(consultant)
        db.session.commit()
        
        app.logger.warning(f'Consultant deleted: {consultant_name} (ID: {consultant_id}), {patients_deleted} patients and {visits_deleted} visits removed')
        
        return jsonify({'success': True, 'message': f'Consultant {consultant_name}, {patients_deleted} patients, and {visits_deleted} visits deleted'})
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error deleting consultant {consultant_id}: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/search_patient_records', methods=['POST'])
def search_patient_records():
    """Search for patient records and visits based on criteria"""
    try:
        data = request.get_json()
        reg_number = data.get('registration_number', '').strip()
        name = data.get('name', '').strip()
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        consultant_ids = data.get('consultant_ids', [])
        
        results = []
        
        # Build base query for visits
        visit_query = Visit.query.join(Patient).join(Consultant)
        
        # Apply filters
        if reg_number:
            visit_query = visit_query.filter(Patient.registration_number.like(f'%{reg_number}%'))
        if name:
            visit_query = visit_query.filter(Patient.full_name.like(f'%{name}%'))
        if start_date:
            visit_query = visit_query.filter(func.date(Visit.visit_date) >= start_date)
        if end_date:
            visit_query = visit_query.filter(func.date(Visit.visit_date) <= end_date)
        if consultant_ids:
            visit_query = visit_query.filter(Visit.consultant_id.in_(consultant_ids))
        
        # Get visits
        visits = visit_query.order_by(Visit.visit_date.desc()).all()
        
        # Add visits to results
        for visit in visits:
            results.append({
                'type': 'visit',
                'id': visit.id,
                'registration_number': visit.patient.registration_number,
                'patient_name': visit.patient.full_name,
                'consultant_name': visit.consultant.name,
                'consultant_color': getattr(visit.consultant, 'color', '#6c757d'),
                'date': visit.visit_date.strftime('%Y-%m-%d %H:%M'),
                'status': visit.status
            })
        
        # Also get unique patients from these visits for patient-level deletion
        patient_ids = list(set(visit.patient_id for visit in visits))
        patients = Patient.query.filter(Patient.id.in_(patient_ids)).all() if patient_ids else []
        
        for patient in patients:
            # Get the first consultant for this patient from filtered visits
            patient_visit = next((v for v in visits if v.patient_id == patient.id), None)
            if patient_visit:
                results.append({
                    'type': 'patient',
                    'id': patient.id,
                    'registration_number': patient.registration_number,
                    'patient_name': patient.full_name,
                    'consultant_name': patient_visit.consultant.name,
                    'consultant_color': getattr(patient_visit.consultant, 'color', '#6c757d'),
                    'date': patient.created_at.strftime('%Y-%m-%d') if hasattr(patient, 'created_at') else 'N/A',
                    'status': f'{len([v for v in visits if v.patient_id == patient.id])} visits'
                })
        
        return jsonify({'success': True, 'results': results})
        
    except Exception as e:
        app.logger.error(f'Error searching patient records: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/delete_record/<record_type>/<int:record_id>', methods=['POST'])
def delete_record(record_type, record_id):
    """Delete a single patient or visit record"""
    try:
        if record_type == 'patient':
            patient = Patient.query.get(record_id)
            if not patient:
                return jsonify({'success': False, 'error': 'Patient not found'})
            
            patient_name = patient.display_name
            # Delete all visits for this patient first
            visits_deleted = Visit.query.filter_by(patient_id=record_id).delete()
            # Then delete the patient record
            db.session.delete(patient)
            db.session.commit()
            
            app.logger.info(f'Patient deleted via admin: {patient_name} (ID: {record_id}), {visits_deleted} visits removed')
            return jsonify({'success': True, 'message': f'Patient {patient_name} and {visits_deleted} visits deleted'})
            
        elif record_type == 'visit':
            visit = Visit.query.get(record_id)
            if not visit:
                return jsonify({'success': False, 'error': 'Visit not found'})
            
            patient_name = visit.patient.display_name
            visit_date = visit.visit_date.strftime('%Y-%m-%d')
            visit_time = visit.visit_date.strftime('%H:%M')
            
            # Only delete the visit record, not the patient
            db.session.delete(visit)
            db.session.commit()
            
            app.logger.info(f'Visit deleted via admin: {patient_name} on {visit_date} at {visit_time} (ID: {record_id})')
            return jsonify({'success': True, 'message': f'Visit for {patient_name} on {visit_date} at {visit_time} deleted'})
        
        else:
            return jsonify({'success': False, 'error': 'Invalid record type'}), 400
            
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error deleting {record_type} record {record_id}: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/delete_multiple_records', methods=['POST'])
def delete_multiple_records():
    """Delete multiple patient or visit records"""
    try:
        data = request.get_json()
        records = data.get('records', [])
        
        if not records:
            return jsonify({'success': False, 'error': 'No records specified'})
        
        deleted_count = 0
        
        for record in records:
            record_type = record.get('type')
            record_id = int(record.get('id'))
            
            if record_type == 'patient':
                patient = Patient.query.get(record_id)
                if patient:
                    # Delete all visits for this patient first
                    Visit.query.filter_by(patient_id=record_id).delete()
                    # Then delete the patient
                    db.session.delete(patient)
                    deleted_count += 1
                    
            elif record_type == 'visit':
                visit = Visit.query.get(record_id)
                if visit:
                    # Only delete the visit, keep the patient record
                    db.session.delete(visit)
                    deleted_count += 1
        
        db.session.commit()
        
        app.logger.info(f'Multiple records deleted via admin: {deleted_count} records')
        return jsonify({'success': True, 'deleted_count': deleted_count})
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error deleting multiple records: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

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

@app.route('/update_patient', methods=['POST'])
def update_patient():
    """Update existing patient information"""
    try:
        patient_id = request.form['patient_id']
        patient = Patient.query.get(patient_id)
        
        if not patient:
            return jsonify({'success': False, 'error': 'Patient not found'}), 404
        
        patient.title = request.form.get('title', '').strip()
        patient.full_name = request.form['full_name'].strip()
        if request.form.get('contact_number'):
            patient.contact_number = request.form['contact_number'].strip()
        if request.form.get('parent_name') is not None:
            patient.parent_name = request.form.get('parent_name', '').strip()
        if request.form.get('email') is not None:
            patient.email = request.form.get('email', '').strip()
        if request.form.get('address'):
            patient.address = request.form.get('address').strip()
        
        db.session.commit()
        app.logger.info(f"Patient updated: {patient.registration_number} - {patient.display_name}")
        
        return jsonify({'success': True, 'message': 'Patient information updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating patient: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
