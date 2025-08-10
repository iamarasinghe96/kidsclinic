#!/usr/bin/env python3
"""
Clinic System Auto-Launcher
Automatically starts server and opens appropriate interface based on laptop role
"""

import os
import sys
import time
import json
import signal
import subprocess
import webbrowser
import threading
from pathlib import Path

# Configuration
SERVER_PORT = 5000
CONFIG_FILE = "clinic_config.json"

def load_config():
    """Load laptop configuration"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"role": "receptionist", "consultant_id": None}

def start_server():
    """Start the Flask server"""
    try:
        # Start gunicorn server
        cmd = ["gunicorn", "--bind", f"0.0.0.0:{SERVER_PORT}", "--reuse-port", "--reload", "main:app"]
        process = subprocess.Popen(cmd, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 cwd=os.getcwd())
        return process
    except Exception as e:
        print(f"Error starting server: {e}")
        return None

def wait_for_server(max_wait=30):
    """Wait for server to be ready"""
    import urllib.request
    
    for i in range(max_wait):
        try:
            urllib.request.urlopen(f"http://localhost:{SERVER_PORT}", timeout=1)
            return True
        except:
            time.sleep(1)
    return False

def open_browser():
    """Open the appropriate interface based on role"""
    config = load_config()
    role = config.get("role", "receptionist")
    consultant_id = config.get("consultant_id")
    
    if role == "consultant" and consultant_id:
        url = f"http://localhost:{SERVER_PORT}/consultant/{consultant_id}"
    else:
        url = f"http://localhost:{SERVER_PORT}/receptionist"
    
    # Wait a bit for server to be fully ready
    time.sleep(2)
    webbrowser.open(url)
    print(f"Opening {role} interface: {url}")

def main():
    """Main launcher function"""
    print("Starting The Kids Clinic Patient Management System...")
    
    config = load_config()
    role = config.get("role", "receptionist")
    
    print(f"Role: {role.upper()}")
    
    # Start the server
    print("Starting server...")
    server_process = start_server()
    
    if not server_process:
        print("Failed to start server!")
        return
    
    # Wait for server to be ready
    print("Waiting for server to start...")
    if not wait_for_server():
        print("Server failed to start properly!")
        server_process.terminate()
        return
    
    print("Server ready!")
    
    # Open browser
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        # Keep the script running
        print("System running. Close the browser to stop the server.")
        print("Press Ctrl+C to stop manually.")
        server_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        if server_process:
            server_process.terminate()
            server_process.wait()
        print("Server stopped.")

if __name__ == "__main__":
    main()