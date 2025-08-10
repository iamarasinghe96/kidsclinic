#!/usr/bin/env python3
"""
Setup script for The Kids Clinic Patient Management System
Run this once after extracting the project files.
"""

import os
import sys

def setup_database():
    """Initialize the database with required tables and default data"""
    try:
        # Set environment variables for database
        os.environ['DATABASE_URL'] = 'sqlite:///clinic.db'
        os.environ['SESSION_SECRET'] = 'clinic-secret-key-2025'
        
        from app import app, db
        from models import Patient, Consultant, Visit
        
        print("Initializing database...")
        
        with app.app_context():
            # Create all tables
            db.create_all()
            
            # Check if consultants already exist
            existing_consultants = Consultant.query.count()
            
            if existing_consultants == 0:
                # Add default consultants
                default_consultants = [
                    {'name': 'Dr. Ajitha Rajapakse', 'consultation_fee': 2500.00, 'color': '#8EC641'},
                    {'name': 'Dr. Sarah Fernando', 'consultation_fee': 2000.00, 'color': '#007bff'},
                    {'name': 'Dr. Nimal Perera', 'consultation_fee': 2200.00, 'color': '#6f42c1'}
                ]
                
                for consultant_data in default_consultants:
                    consultant = Consultant(**consultant_data)
                    db.session.add(consultant)
                
                db.session.commit()
                print(f"Added {len(default_consultants)} default consultants")
            else:
                print(f"Found {existing_consultants} existing consultants")
        
        print("✓ Database initialized successfully!")
        print(f"✓ Database file created: {os.path.abspath('clinic.db')}")
        return True
        
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        return False

def main():
    print("=" * 60)
    print("The Kids Clinic Patient Management System - Setup")
    print("=" * 60)
    
    # Check if we're in the right directory
    required_files = ['app.py', 'models.py', 'main.py', 'routes.py']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print("✗ Error: Missing required files:")
        for file in missing_files:
            print(f"  - {file}")
        print("\nPlease ensure you're running this script from the project directory.")
        return False
    
    print("✓ All required files found")
    
    # Setup database
    if setup_database():
        print("\n" + "=" * 60)
        print("Setup completed successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Note your computer's IP address for network setup")
        print("2. Create startup shortcuts using the README instructions")
        print("3. Test the system by running the startup shortcut")
        print("\nTo start manually: python -m gunicorn --bind 0.0.0.0:5000 main:app")
        return True
    else:
        print("\n✗ Setup failed. Please check the error messages above.")
        return False

if __name__ == "__main__":
    success = main()
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)