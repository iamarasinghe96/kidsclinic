#!/usr/bin/env python3
"""
Database migration script to add consultation_fee column to consultant table
"""
import sqlite3
import os

def migrate_database():
    # Path to the database file
    db_path = 'clinic.db'
    
    if not os.path.exists(db_path):
        print("Database file not found. Creating new database with updated schema.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if consultation_fee column already exists
        cursor.execute("PRAGMA table_info(consultant)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'consultation_fee' not in columns:
            print("Adding consultation_fee column to consultant table...")
            cursor.execute('ALTER TABLE consultant ADD COLUMN consultation_fee REAL DEFAULT 0.0')
            conn.commit()
            print("Migration completed successfully!")
        else:
            print("consultation_fee column already exists.")
            
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()