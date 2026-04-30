import os
import time
import logging
import urllib.request
import json
from datetime import date
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "clinic-management-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the SQLite database (relative path for cross-platform compatibility)
import os
database_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clinic.db')
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_path}"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

def format_datetime(dt):
    """Format datetime as DD/MM - H:MM AM/PM"""
    return dt.strftime('%d/%m - %I:%M %p')

# Add filter to Jinja2 environment
app.jinja_env.filters['datetime'] = format_datetime

# Unique ID stamped into every page so browsers detect a server restart
# and hard-reload instead of serving cached JavaScript
SERVER_BOOT_ID = str(int(time.time()))
app.jinja_env.globals['server_boot_id'] = SERVER_BOOT_ID

@app.after_request
def no_cache(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# ---------- Holiday theme system ----------

THEME_KEYWORDS = [
    ('vesak',        'vesak'),
    ('christmas',    'christmas'),
    ('pongal',       'pongal'),
    ('eid',          'islamic'),
    ('milad',        'islamic'),
    ('ramadan',      'islamic'),
    ('deepavali',    'deepavali'),
    ('sinhala',      'new_year'),
    ('avurudu',      'new_year'),
    ('independence', 'independence'),
    ('sivarathri',   'hindu'),
    ('good friday',  'christian'),
]

_holiday_cache = {'date': None, 'theme': 'default', 'name': None}


def get_today_holiday():
    # Allow start.bat to force a specific theme for testing
    test_theme = os.environ.get('HOLIDAY_THEME_TEST', '').strip()
    if test_theme:
        name_map = {
            'christmas':    'Christmas Day (test)',
            'poya':         'Full Moon Poya Day (test)',
            'vesak':        'Vesak Full Moon Poya Day (test)',
            'pongal':       'Thai Pongal (test)',
            'islamic':      'Eid ul-Fitr (test)',
            'deepavali':    'Deepavali (test)',
            'new_year':     'Sinhala & Tamil New Year (test)',
            'independence': 'Independence Day (test)',
            'hindu':        'Maha Sivarathri (test)',
            'christian':    'Good Friday (test)',
            'public_holiday': 'Public Holiday (test)',
            'default':      None,
        }
        return {'date': None, 'theme': test_theme, 'name': name_map.get(test_theme)}

    today = date.today()
    if _holiday_cache['date'] == today:
        return _holiday_cache
    try:
        url = (
            f'https://raw.githubusercontent.com/Dilshan-H/srilanka-holidays'
            f'/main/json/{today.year}.json'
        )
        with urllib.request.urlopen(url, timeout=5) as r:
            holidays = json.loads(r.read())
    except Exception:
        holidays = []
    today_str = today.isoformat()
    for h in holidays:
        if h['start'] <= today_str < h['end']:
            name = h['summary']
            cats = h.get('categories', [])
            name_lower = name.lower()
            theme = 'public_holiday'
            if 'Poya' in cats:
                theme = 'vesak' if 'vesak' in name_lower else 'poya'
            else:
                for kw, t in THEME_KEYWORDS:
                    if kw in name_lower:
                        theme = t
                        break
            _holiday_cache.update({'date': today, 'theme': theme, 'name': name})
            return _holiday_cache
    _holiday_cache.update({'date': today, 'theme': 'default', 'name': None})
    return _holiday_cache


@app.context_processor
def inject_holiday():
    h = get_today_holiday()
    return {'today_theme': h['theme'], 'today_holiday': h['name']}


@app.route('/clinic-logo.png')
def clinic_logo():
    return send_from_directory('templates', 'removed-bg.png')

@app.route('/flag-lk.png')
def flag_lk():
    return send_from_directory('templates', '1f1f1-1f1f0.png')

with app.app_context():
    # Import models and routes
    import models
    import routes
    
    # Create all tables
    db.create_all()
    
    # Initialize default consultants if none exist
    from models import Consultant
    try:
        if not Consultant.query.first():
            default_consultants = [
                ("Dr. John Smith", 5000.0),
                ("Dr. Sarah Johnson", 4500.0), 
                ("Dr. Michael Brown", 5500.0),
                ("Dr. Emily Davis", 4000.0),
                ("Dr. David Wilson", 6000.0),
                ("Dr. Lisa Garcia", 5500.0)
            ]
            for name, fee in default_consultants:
                consultant = Consultant(name=name, consultation_fee=fee)
                db.session.add(consultant)
            db.session.commit()
            logging.info("Default consultants created with consultation fees")
    except Exception as e:
        # Handle database issues gracefully during migration
        logging.warning(f"Database initialization issue: {e}")
        db.session.rollback()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
