#!/usr/bin/env python3
"""
Database initialization script for the clinic management system.
This script will create a fresh database with all required tables and default data.
"""

import os
import sys
from app import app, db
from models import Consultant, Patient, Visit

def init_database():
    """Initialize the database with fresh schema and default data"""
    
    with app.app_context():
        print("Initializing database...")
        
        # Remove existing database file
        db_path = 'clinic.db'
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"Removed existing database: {db_path}")
        
        # Create all tables
        db.create_all()
        print("Created all database tables")
        
        # First check if color column exists and add it if not
        import sqlite3
        conn = sqlite3.connect('clinic.db')
        cursor = conn.cursor()
        
        try:
            # Check if color column exists
            cursor.execute("PRAGMA table_info(consultant)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'color' not in columns:
                print("Adding color column to consultant table...")
                cursor.execute('ALTER TABLE consultant ADD COLUMN color VARCHAR(7) DEFAULT "#6c757d"')
                conn.commit()
                print("Color column added successfully")
            else:
                print("Color column already exists")
                
        except Exception as e:
            print(f"Error checking/adding color column: {e}")
        finally:
            conn.close()
        
        # Add default consultants with colors
        default_consultants = [
            ('Dr. John Smith', 5000.0, '#007bff'),
            ('Dr. Sarah Johnson', 4500.0, '#28a745'), 
            ('Dr. Michael Brown', 5500.0, '#dc3545'),
            ('Dr. Emily Davis', 4000.0, '#fd7e14'),
            ('Dr. David Wilson', 6000.0, '#6f42c1'),
            ('Dr. Lisa Garcia', 5500.0, '#20c997')
        ]
        
        for name, fee, color in default_consultants:
            consultant = Consultant(name=name, consultation_fee=fee, color=color)
            db.session.add(consultant)
        
        db.session.commit()
        print(f"Added {len(default_consultants)} default consultants")
        
        # Verify the setup
        consultants = Consultant.query.all()
        print("\nCreated consultants:")
        for c in consultants:
            print(f"  - {c.name}: {c.color} (Fee: ₹{c.consultation_fee})")
        
        print("\nDatabase initialization completed successfully!")
        return True

if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)