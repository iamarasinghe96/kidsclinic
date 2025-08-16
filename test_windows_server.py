#!/usr/bin/env python3
"""
Windows-compatible clinic server - NO GUNICORN
Pure Flask development server only
"""

import sys
import webbrowser
from threading import Timer

def open_browser():
    """Open browser to receptionist interface"""
    try:
        webbrowser.open('http://localhost:5000/receptionist')
    except:
        pass

def main():
    print("Starting The Kids Clinic Management System...")
    print("=" * 50)
    
    try:
        # Import Flask app
        from app import app
        print("✓ Flask app loaded successfully")
        
        # Start browser after 2 seconds
        Timer(2.0, open_browser).start()
        
        print("Server starting on: http://0.0.0.0:5000")
        print("Receptionist: http://localhost:5000/receptionist")
        print("Consultant: http://YOUR_IP:5000/consultant")
        print("Reports: http://YOUR_IP:5000/report")
        print("Admin: http://YOUR_IP:5000/admin")
        print("")
        print("Press Ctrl+C to stop server")
        print("=" * 50)
        
        # Start Flask server (NO GUNICORN)
        app.run(
            host='0.0.0.0',      # Network access
            port=5000,           # Standard port
            debug=False,         # Production mode
            use_reloader=False,  # No auto-reload
            threaded=True        # Handle multiple requests
        )
        
    except KeyboardInterrupt:
        print("\n\nServer stopped by user. Goodbye!")
        sys.exit(0)
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("Make sure all required files are present:")
        print("- app.py, models.py, routes.py")
        print("- templates/ folder")
        print("- clinic.db file")
        input("Press Enter to exit...")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Server error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == '__main__':
    main()