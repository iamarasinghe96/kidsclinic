
#!/usr/bin/env python3
"""
Desktop shortcut creator for Clinic Management System - Consultant Laptop
"""
import os
import sys
import platform
import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog
import webbrowser
import time

def install_windows_dependencies():
    """Install Windows-specific dependencies if not available"""
    try:
        import winshell
        import win32com.client
        return True
    except ImportError:
        print("Installing Windows dependencies...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pywin32', 'winshell'])
            print("✅ Windows dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install Windows dependencies automatically")
            print("Please run: pip install pywin32 winshell")
            return False

def get_server_ip():
    """Get the server IP address from user"""
    root = tk.Tk()
    root.withdraw()
    
    ip = simpledialog.askstring(
        "Receptionist's IP Address", 
        "Enter the IP address shown on the receptionist's laptop:\n\nExample: 192.168.1.100",
        initialvalue=""
    )
    root.destroy()
    return ip if ip else "192.168.1.100"

def create_windows_shortcut(name, url):
    """Create a Windows desktop shortcut that opens URL directly"""
    if not install_windows_dependencies():
        return None
        
    import winshell
    from win32com.client import Dispatch
    
    desktop = winshell.desktop()
    shortcut_path = os.path.join(desktop, f"{name}.lnk")
    
    # Create batch file that opens URL in default browser
    batch_dir = os.path.join(os.getcwd(), "shortcuts")
    os.makedirs(batch_dir, exist_ok=True)
    batch_file = os.path.join(batch_dir, f"{name.replace(' ', '_').replace('-', '_')}.bat")
    
    batch_content = f'''@echo off
title {name}
echo Opening {name}...
start "" "{url}"
'''
    
    with open(batch_file, 'w') as f:
        f.write(batch_content)
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.TargetPath = batch_file
    shortcut.WorkingDirectory = os.getcwd()
    shortcut.Description = f"{name} - Clinic Management System"
    
    shortcut.Save()
    return shortcut_path

def create_macos_shortcut(name, url):
    """Create a macOS shortcut"""
    desktop = os.path.expanduser("~/Desktop")
    app_name = f"{name}.app"
    app_path = os.path.join(desktop, app_name)
    
    os.makedirs(os.path.join(app_path, "Contents", "MacOS"), exist_ok=True)
    os.makedirs(os.path.join(app_path, "Contents", "Resources"), exist_ok=True)
    
    info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>CFBundleIdentifier</key>
    <string>com.clinic.{name.lower().replace(' ', '')}</string>
    <key>CFBundleName</key>
    <string>{name}</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
</dict>
</plist>"""
    
    with open(os.path.join(app_path, "Contents", "Info.plist"), "w") as f:
        f.write(info_plist)
    
    launcher_script = f"""#!/bin/bash
open "{url}"
"""
    
    launcher_path = os.path.join(app_path, "Contents", "MacOS", "launcher")
    with open(launcher_path, "w") as f:
        f.write(launcher_script)
    
    os.chmod(launcher_path, 0o755)
    return app_path

def create_linux_shortcut(name, url):
    """Create a Linux desktop shortcut"""
    desktop = os.path.expanduser("~/Desktop")
    shortcut_path = os.path.join(desktop, f"{name}.desktop")
    
    shortcut_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={name}
Comment=Clinic Management System - {name}
Exec=xdg-open "{url}"
Icon=applications-internet
Terminal=false
Categories=Office;
"""
    
    with open(shortcut_path, "w") as f:
        f.write(shortcut_content)
    
    os.chmod(shortcut_path, 0o755)
    return shortcut_path

def main():
    """Main function to create desktop shortcuts"""
    print("🏥 Clinic Management System - Consultant Shortcuts")
    print("=" * 60)
    
    server_ip = get_server_ip()
    base_url = f"http://{server_ip}:5000"
    
    print(f"Server URL: {base_url}")
    
    shortcuts = [
        ("Reception - Clinic Management", f"{base_url}/reception"),
        ("Reports - Clinic Management", f"{base_url}/report"),
        ("Consultant 1 - Clinic Management", f"{base_url}/consultant?consultant_id=1"),
        ("Consultant 2 - Clinic Management", f"{base_url}/consultant?consultant_id=2"),
        ("Consultant 3 - Clinic Management", f"{base_url}/consultant?consultant_id=3")
    ]
    
    created_shortcuts = []
    system = platform.system()
    
    try:
        for name, url in shortcuts:
            print(f"Creating shortcut: {name}")
            
            if system == "Windows":
                shortcut_path = create_windows_shortcut(name, url)
            elif system == "Darwin":
                shortcut_path = create_macos_shortcut(name, url)
            elif system == "Linux":
                shortcut_path = create_linux_shortcut(name, url)
            else:
                print(f"Unsupported operating system: {system}")
                continue
            
            if shortcut_path:
                created_shortcuts.append(shortcut_path)
                print(f"✅ Created: {shortcut_path}")
    
    except Exception as e:
        print(f"❌ Error creating shortcuts: {str(e)}")
        return
    
    print(f"\n🎉 Successfully created {len(created_shortcuts)} desktop shortcuts!")
    print(f"\n📋 Shortcuts connect to server: {server_ip}")
    print("Double-click any shortcut to access the clinic system")

if __name__ == "__main__":
    main()
