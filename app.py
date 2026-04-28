import os
import logging
from flask import Flask
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

@app.after_request
def no_cache(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

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
