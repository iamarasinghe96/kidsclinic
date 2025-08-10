from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "clinic-management-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///clinic.db"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy()
db.init_app(app)

def format_datetime(dt):
    """Format datetime as DD/MM - H:MM AM/PM"""
    return dt.strftime('%d/%m - %I:%M %p')

# Add filter to Jinja2 environment
app.jinja_env.filters['datetime'] = format_datetime

with app.app_context():
    # Import models and routes
    import models
    import routes

    # Create all tables
    db.create_all()

    # Initialize default consultants if none exist
    from models import Consultant
    if not Consultant.query.first():
        default_consultants = [
            ("Dr. John Smith", 5000.0),
            ("Dr. Sarah Johnson", 4500.0),
            ("Dr. Michael Brown", 5500.0),
            ("Dr. Emily Davis", 4000.0),
            ("Dr. David Wilson", 6000.0)
        ]
        for name, fee in default_consultants:
            consultant = Consultant(name=name, consultation_fee=fee)
            db.session.add(consultant)
        db.session.commit()
        logging.info("Default consultants created with consultation fees")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)