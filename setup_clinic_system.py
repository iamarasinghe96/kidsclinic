#!/usr/bin/env python3
"""
Clinic System Setup Script
Creates role-based shortcuts for consultant and receptionist laptops
"""

import os
import sys
import json
import subprocess
import platform
from pathlib import Path

# Configuration file to store laptop role
CONFIG_FILE = "clinic_config.json"

def get_system_type():
    """Detect the operating system"""
    system = platform.system().lower()
    return system

def create_windows_shortcut(name, target, arguments="", icon_path=None):
    """Create a Windows shortcut"""
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        shortcut_path = os.path.join(desktop, f"{name}.lnk")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target
        shortcut.Arguments = arguments
        shortcut.WorkingDirectory = os.path.dirname(target)
        if icon_path:
            shortcut.IconLocation = icon_path
        shortcut.save()
        
        return shortcut_path
    except ImportError:
        print("Windows shortcut creation requires winshell and pywin32 packages")
        return None

def create_linux_desktop_file(name, target, arguments="", icon_path=None):
    """Create a Linux desktop file"""
    desktop_dir = os.path.expanduser("~/Desktop")
    if not os.path.exists(desktop_dir):
        os.makedirs(desktop_dir)
    
    desktop_file_path = os.path.join(desktop_dir, f"{name}.desktop")
    
    content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={name}
Comment=The Kids Clinic Patient Management System - {name}
Exec=python3 "{target}" {arguments}
Icon={icon_path or "application-x-executable"}
Terminal=false
StartupNotify=true
Categories=Office;Medical;
"""
    
    with open(desktop_file_path, 'w') as f:
        f.write(content)
    
    # Make executable
    os.chmod(desktop_file_path, 0o755)
    return desktop_file_path

def create_macos_app(name, target, arguments=""):
    """Create a macOS app bundle"""
    app_dir = os.path.expanduser(f"~/Desktop/{name}.app")
    contents_dir = os.path.join(app_dir, "Contents")
    macos_dir = os.path.join(contents_dir, "MacOS")
    
    os.makedirs(macos_dir, exist_ok=True)
    
    # Create Info.plist
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>{name}</string>
    <key>CFBundleIdentifier</key>
    <string>com.clinic.{name.lower().replace(' ', '')}</string>
    <key>CFBundleName</key>
    <string>{name}</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
</dict>
</plist>"""
    
    with open(os.path.join(contents_dir, "Info.plist"), 'w') as f:
        f.write(plist_content)
    
    # Create executable script
    script_content = f"""#!/bin/bash
cd "{os.getcwd()}"
python3 "{target}" {arguments}
"""
    
    script_path = os.path.join(macos_dir, name)
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    os.chmod(script_path, 0o755)
    return app_dir

def save_config(role, consultant_id=None):
    """Save the laptop role configuration"""
    config = {
        "role": role,
        "consultant_id": consultant_id,
        "setup_date": str(os.path.getctime(__file__) if os.path.exists(__file__) else "unknown")
    }
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Configuration saved: {role} laptop")

def load_config():
    """Load the existing configuration"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return None

def get_consultants():
    """Get list of consultants from database"""
    try:
        # Import here to avoid issues if not in right directory
        sys.path.append(os.getcwd())
        from app import app, db
        from models import Consultant
        
        with app.app_context():
            consultants = Consultant.query.all()
            return [(c.id, c.name) for c in consultants]
    except Exception as e:
        print(f"Could not load consultants: {e}")
        return [(1, "Dr. Default")]

def setup_laptop():
    """Main setup function"""
    print("=" * 60)
    print("  THE KIDS CLINIC / ALLERGY AND ASTHMA CENTER")
    print("            Patient Management System Setup")
    print("=" * 60)
    print()
    
    # Check for existing configuration
    existing_config = load_config()
    if existing_config:
        print(f"This laptop is already configured as: {existing_config['role'].upper()}")
        print(f"Consultant ID: {existing_config.get('consultant_id', 'N/A')}")
        print()
        reconfigure = input("Do you want to reconfigure? (y/N): ").lower().strip()
        if reconfigure != 'y':
            print("Setup cancelled.")
            return
        print()
    
    print("Please select the laptop role:")
    print("1. Consultant Laptop (View-only patient queues)")
    print("2. Receptionist Laptop (Full patient management)")
    print()
    
    while True:
        choice = input("Enter your choice (1 or 2): ").strip()
        if choice in ['1', '2']:
            break
        print("Please enter 1 or 2")
    
    if choice == '1':
        # Consultant setup
        print("\nSetting up CONSULTANT laptop...")
        print("Available consultants:")
        
        consultants = get_consultants()
        for idx, (c_id, c_name) in enumerate(consultants, 1):
            print(f"{idx}. {c_name}")
        
        while True:
            try:
                consultant_choice = int(input(f"\nSelect consultant (1-{len(consultants)}): "))
                if 1 <= consultant_choice <= len(consultants):
                    consultant_id, consultant_name = consultants[consultant_choice - 1]
                    break
                print(f"Please enter a number between 1 and {len(consultants)}")
            except ValueError:
                print("Please enter a valid number")
        
        role = "consultant"
        save_config(role, consultant_id)
        
        # Create launcher script
        launcher_script = "start_clinic_system.py"
        create_launcher_script(launcher_script, role, consultant_id)
        
        # Create desktop shortcuts
        system_type = get_system_type()
        shortcut_name = f"Clinic - Dr. {consultant_name}"
        
        if system_type == "windows":
            create_windows_shortcut(shortcut_name, sys.executable, f'"{launcher_script}"')
        elif system_type == "linux":
            create_linux_desktop_file(shortcut_name, launcher_script)
        elif system_type == "darwin":  # macOS
            create_macos_app(shortcut_name, launcher_script)
        
        print(f"\n✓ Consultant laptop setup complete!")
        print(f"✓ Desktop shortcut created: {shortcut_name}")
        print(f"✓ Assigned to: Dr. {consultant_name}")
        
    else:
        # Receptionist setup
        print("\nSetting up RECEPTIONIST laptop...")
        role = "receptionist"
        save_config(role)
        
        # Create launcher script
        launcher_script = "start_clinic_system.py"
        create_launcher_script(launcher_script, role)
        
        # Create desktop shortcuts
        system_type = get_system_type()
        shortcut_name = "Clinic - Receptionist"
        
        if system_type == "windows":
            create_windows_shortcut(shortcut_name, sys.executable, f'"{launcher_script}"')
        elif system_type == "linux":
            create_linux_desktop_file(shortcut_name, launcher_script)
        elif system_type == "darwin":  # macOS
            create_macos_app(shortcut_name, launcher_script)
        
        print(f"\n✓ Receptionist laptop setup complete!")
        print(f"✓ Desktop shortcut created: {shortcut_name}")
        print(f"✓ Full patient management access enabled")
    
    print("\nSetup Instructions:")
    print("1. Double-click the desktop shortcut to start the clinic system")
    print("2. The server will start automatically and open the appropriate interface")
    print("3. Close the browser window to stop the server automatically")
    print("\nThe system is ready to use!")

def create_launcher_script(filename, role, consultant_id=None):
    """Create the launcher script that starts the server and opens browser"""
    script_content = f'''#!/usr/bin/env python3
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
    return {{"role": "{role}", "consultant_id": {consultant_id}}}

def start_server():
    """Start the Flask server"""
    try:
        # Start gunicorn server
        cmd = ["gunicorn", "--bind", f"0.0.0.0:{{SERVER_PORT}}", "--reuse-port", "--reload", "main:app"]
        process = subprocess.Popen(cmd, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 cwd=os.getcwd())
        return process
    except Exception as e:
        print(f"Error starting server: {{e}}")
        return None

def wait_for_server(max_wait=30):
    """Wait for server to be ready"""
    import urllib.request
    
    for i in range(max_wait):
        try:
            urllib.request.urlopen(f"http://localhost:{{SERVER_PORT}}", timeout=1)
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
        url = f"http://localhost:{{SERVER_PORT}}/consultant/{{consultant_id}}"
    else:
        url = f"http://localhost:{{SERVER_PORT}}/receptionist"
    
    # Wait a bit for server to be fully ready
    time.sleep(2)
    webbrowser.open(url)
    print(f"Opening {{role}} interface: {{url}}")

def main():
    """Main launcher function"""
    print("Starting The Kids Clinic Patient Management System...")
    
    config = load_config()
    role = config.get("role", "receptionist")
    
    print(f"Role: {{role.upper()}}")
    
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
        print("\\nShutting down...")
    finally:
        if server_process:
            server_process.terminate()
            server_process.wait()
        print("Server stopped.")

if __name__ == "__main__":
    main()
'''
    
    with open(filename, 'w') as f:
        f.write(script_content)
    
    # Make executable on Unix systems
    if os.name != 'nt':
        os.chmod(filename, 0o755)

if __name__ == "__main__":
    setup_laptop()