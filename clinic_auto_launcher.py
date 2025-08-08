
#!/usr/bin/env python3
"""
Clinic Management System - All-in-One Auto Launcher
This script automatically starts the server and opens the appropriate interface
"""
import os
import sys
import time
import subprocess
import webbrowser
import socket
import tkinter as tk
from tkinter import messagebox
import threading
import requests

def check_server_running(host='127.0.0.1', port=5000):
    """Check if server is already running"""
    try:
        response = requests.get(f'http://{host}:{port}', timeout=2)
        return True
    except:
        return False

def wait_for_server(host='127.0.0.1', port=5000, timeout=30):
    """Wait for server to start"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_server_running(host, port):
            return True
        time.sleep(1)
    return False

def start_server():
    """Start the Flask server if not running"""
    if check_server_running():
        print("✅ Server is already running")
        return True
    
    print("🚀 Starting server...")
    try:
        # Start server in background
        if sys.platform.startswith('win'):
            subprocess.Popen([sys.executable, "main.py"], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen([sys.executable, "main.py"])
        
        # Wait for server to start
        if wait_for_server():
            print("✅ Server started successfully!")
            return True
        else:
            print("❌ Server failed to start")
            return False
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

def open_interface(interface_type):
    """Open the specified interface"""
    urls = {
        'reception': 'http://127.0.0.1:5000/reception',
        'reports': 'http://127.0.0.1:5000/report',
        'consultant': 'http://127.0.0.1:5000/consultant'
    }
    
    if interface_type in urls:
        print(f"🌐 Opening {interface_type} interface...")
        webbrowser.open(urls[interface_type])
    else:
        print(f"❌ Unknown interface type: {interface_type}")

def launch_clinic_system(interface='reception', consultant_id=None):
    """Main launcher function"""
    print("🏥 Clinic Management System - Auto Launcher")
    print("=" * 50)
    
    # Start server if needed
    if not start_server():
        input("❌ Failed to start server. Press Enter to exit...")
        return
    
    # Wait a moment for server to fully initialize
    time.sleep(2)
    
    # Open appropriate interface
    if interface == 'consultant' and consultant_id:
        url = f'http://127.0.0.1:5000/consultant?consultant_id={consultant_id}'
        print(f"🌐 Opening Consultant {consultant_id} interface...")
        webbrowser.open(url)
    else:
        open_interface(interface)
    
    print("✅ Clinic system launched successfully!")
    print("💡 Keep this window open while using the system")
    
    # Keep script running
    try:
        input("\nPress Enter to exit...")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    # Parse command line arguments
    interface = 'reception'
    consultant_id = None
    
    if len(sys.argv) > 1:
        interface = sys.argv[1]
    if len(sys.argv) > 2:
        consultant_id = sys.argv[2]
    
    launch_clinic_system(interface, consultant_id)
