#!/usr/bin/env python3
"""
Debug script to test report functionality
"""

from app import app, db
from models import Visit, Patient, Consultant
from sqlalchemy import func, text
from datetime import datetime, date

def test_report_query():
    with app.app_context():
        print("=== Debug Report Query ===")
        
        # Test dates
        start_date = date(2025, 8, 8)
        end_date = date(2025, 8, 16)
        
        print(f"Testing date range: {start_date} to {end_date}")
        
        # Raw count
        total_visits = Visit.query.count()
        print(f"Total visits in database: {total_visits}")
        
        # Try different query approaches
        print("\n1. SQLAlchemy ORM query:")
        try:
            visits_orm = Visit.query.join(Patient).filter(
                func.date(Visit.visit_date) >= start_date,
                func.date(Visit.visit_date) <= end_date
            ).all()
            print(f"   Found {len(visits_orm)} visits")
        except Exception as e:
            print(f"   Error: {e}")
        
        print("\n2. Raw SQL query:")
        try:
            result = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM visit v 
                JOIN patient p ON v.patient_id = p.id 
                WHERE DATE(v.visit_date) >= :start_date 
                AND DATE(v.visit_date) <= :end_date
            """), {'start_date': start_date, 'end_date': end_date})
            count = result.scalar()
            print(f"   Found {count} visits")
        except Exception as e:
            print(f"   Error: {e}")
        
        print("\n3. Direct date comparison:")
        try:
            visits_direct = Visit.query.filter(
                Visit.visit_date >= datetime.combine(start_date, datetime.min.time()),
                Visit.visit_date <= datetime.combine(end_date, datetime.max.time())
            ).all()
            print(f"   Found {len(visits_direct)} visits")
            if visits_direct:
                print("   Sample visits:")
                for v in visits_direct[:3]:
                    print(f"     {v.visit_date} - {v.patient.full_name} ({v.status})")
        except Exception as e:
            print(f"   Error: {e}")
        
        print("\n4. Check visit date range:")
        try:
            min_date = db.session.execute(text("SELECT MIN(visit_date) FROM visit")).scalar()
            max_date = db.session.execute(text("SELECT MAX(visit_date) FROM visit")).scalar()
            print(f"   Visit dates range from {min_date} to {max_date}")
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    test_report_query()