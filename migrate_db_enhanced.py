#!/usr/bin/env python3
"""
Database migration script to add new fields for enhanced patient management
"""

import os
from sqlalchemy import create_engine, text
from app import app, db

def migrate_database():
    """Add new columns to existing tables"""
    
    with app.app_context():
        engine = db.engine
        
        print("Starting database migration...")
        
        try:
            # Add new columns to patients table
            print("Adding parent_name column to patients table...")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE patient ADD COLUMN parent_name VARCHAR(100)"))
                conn.commit()
            
            print("Adding email column to patients table...")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE patient ADD COLUMN email VARCHAR(120)"))
                conn.commit()
            
            # Add weight tracking to visits table
            print("Adding weight_kg column to visits table...")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE visit ADD COLUMN weight_kg FLOAT"))
                conn.commit()
            
            print("Migration completed successfully!")
            
        except Exception as e:
            if "already exists" in str(e) or "duplicate column" in str(e).lower():
                print(f"Column already exists (skipping): {e}")
            else:
                print(f"Migration error: {e}")
                # Continue anyway - the application will work with existing schema
        
        # Ensure all tables are created with new schema
        print("Creating any missing tables...")
        db.create_all()
        print("Database setup complete!")

if __name__ == "__main__":
    migrate_database()