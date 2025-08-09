
from app import app
import os

if __name__ == '__main__':
    print("🏥 Clinic Management System - Server Starting...")
    print("=" * 50)
    
    # Get local IP for display
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "127.0.0.1"
    
    print(f"✅ Server will start on: {local_ip}:5000")
    print(f"📋 Reception URL: http://{local_ip}:5000/reception")
    print(f"📊 Reports URL: http://{local_ip}:5000/report")
    print()
    print("📝 IMPORTANT FOR CONSULTANT LAPTOP:")
    print(f"   Tell the consultant to use IP: {local_ip}")
    print()
    print("🌐 Starting web server...")
    print("=" * 50)
    
    # Auto-open reception page
    import webbrowser
    import threading
    import time
    
    def open_browser():
        time.sleep(2)  # Wait for server to start
        webbrowser.open(f"http://127.0.0.1:5000/reception")
    
    threading.Thread(target=open_browser).start()
    
    app.run(host='0.0.0.0', port=5000, debug=False)
