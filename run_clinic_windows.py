#!/usr/bin/env python3
"""
Windows-compatible clinic server launcher
No gunicorn dependency - uses Flask's built-in server
"""

import sys
import time
import webbrowser
from threading import Timer
from app import app

def open_browser():
    """Open browser after short delay"""
    webbrowser.open('http://localhost:5000/receptionist')
    # Small delay between opening tabs
    time.sleep(1)
    webbrowser.open('http://localhost:5000/queue_management')

def main():
    print("=" * 50)
    print("  THE KIDS CLINIC - RECEPTIONIST SYSTEM")
    print("=" * 50)
    print()
    print("Starting server on IP: 0.0.0.0:5000")
    print("Local access: http://localhost:5000/receptionist")
    print("Consultant access: http://YOUR_IP:5000/consultant")
    print("Reports: http://YOUR_IP:5000/report")
    print("Admin: http://YOUR_IP:5000/admin")
    print()
    print("Opening receptionist interface and queue management in 3 seconds...")
    print()
    print("Server is running... Do NOT close this window!")
    print("To stop server: Press Ctrl+C")
    print()
    
    # Open browser after 3 seconds
    Timer(3.0, open_browser).start()
    
    try:
        # Run Flask server with network access
        app.run(
            host='0.0.0.0',  # Allow network access
            port=5000,
            debug=False,     # Production mode
            use_reloader=False  # Prevent double startup
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError starting server: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == '__main__':
    main()