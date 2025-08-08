
#!/usr/bin/env python3
"""
Desktop shortcut creator for Clinic Management System
Creates shortcuts for Reception and Consultant interfaces
"""
import os
import sys
import platform
import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog

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
    root.withdraw()  # Hide the main window
    
    ip = simpledialog.askstring(
        "Server IP Address", 
        "Enter the IP address of the receptionist's laptop\n(where the database server is running):\n\nExample: 192.168.1.100\nLeave empty if this IS the server laptop:",
        initialvalue=""
    )
    root.destroy()
    return ip if ip else "localhost"

def create_windows_shortcut(name, url, icon_path=None):
    """Create a Windows desktop shortcut"""
    if not install_windows_dependencies():
        return None
        
    import winshell
    from win32com.client import Dispatch
    
    desktop = winshell.desktop()
    shortcut_path = os.path.join(desktop, f"{name}.lnk")
    
    # Create a batch file that starts server and opens browser
    batch_dir = os.path.join(os.getcwd(), "shortcuts")
    os.makedirs(batch_dir, exist_ok=True)
    batch_file = os.path.join(batch_dir, f"{name.replace(' ', '_').replace('-', '_')}.bat")
    
    # Get launcher command from shortcut info
    launcher_cmd = ""
    for shortcut_info in shortcuts:
        if len(shortcut_info) >= 3 and shortcut_info[0] == name:
            launcher_cmd = shortcut_info[2]
            break
    
    # Create smart batch file using auto-launcher
    batch_content = f'''@echo off
title {name}
cd /d "{os.getcwd()}"
python clinic_auto_launcher.py {launcher_cmd}
'''
    
    with open(batch_file, 'w') as f:
        f.write(batch_content)
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.TargetPath = batch_file
    shortcut.WorkingDirectory = os.getcwd()
    shortcut.Description = f"Auto-start {name} - Clinic Management System"
    
    if icon_path and os.path.exists(icon_path):
        shortcut.IconLocation = icon_path
    
    shortcut.Save()
    return shortcut_path

def create_macos_shortcut(name, url):
    """Create a macOS desktop shortcut"""
    desktop = os.path.expanduser("~/Desktop")
    app_name = f"{name}.app"
    app_path = os.path.join(desktop, app_name)
    
    # Create app bundle structure
    os.makedirs(os.path.join(app_path, "Contents", "MacOS"), exist_ok=True)
    os.makedirs(os.path.join(app_path, "Contents", "Resources"), exist_ok=True)
    
    # Create Info.plist
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
    
    # Create launcher script
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
    print("🏥 Clinic Management System - Desktop Shortcut Creator")
    print("=" * 60)
    
    # Get server IP
    server_ip = get_server_ip()
    base_url = f"http://{server_ip}:5000"
    
    print(f"Server URL: {base_url}")
    
    # Define shortcuts to create with launcher commands
    shortcuts = [
        ("Reception - Clinic Management", f"{base_url}/reception", "reception"),
        ("Reports - Clinic Management", f"{base_url}/report", "reports")
    ]
    
    # Add consultant shortcuts (you can modify consultant IDs as needed)
    for i in range(1, 6):  # Assuming 5 consultants with IDs 1-5
        shortcuts.append((f"Consultant {i} - Clinic Management", f"{base_url}/consultant?consultant_id={i}", f"consultant {i}"))
    
    created_shortcuts = []
    system = platform.system()
    
    try:
        for shortcut_info in shortcuts:
            name = shortcut_info[0]
            url = shortcut_info[1]
            print(f"Creating shortcut: {name}")
            
            if system == "Windows":
                shortcut_path = create_windows_shortcut(name, url)
            elif system == "Darwin":  # macOS
                shortcut_path = create_macos_shortcut(name, url)
            elif system == "Linux":
                shortcut_path = create_linux_shortcut(name, url)
            else:
                print(f"Unsupported operating system: {system}")
                continue
            
            if shortcut_path:
                created_shortcuts.append(shortcut_path)
                print(f"✅ Created: {shortcut_path}")
            else:
                print(f"❌ Failed to create: {name}")
    
    except Exception as e:
        print(f"❌ Error creating shortcuts: {str(e)}")
        if system == "Windows":
            print("\n📝 Note: On Windows, you may need to install 'pywin32' and 'winshell':")
            print("pip install pywin32 winshell")
        return
    
    print(f"\n🎉 Successfully created {len(created_shortcuts)} desktop shortcuts!")
    print("\n📋 Next steps:")
    print(f"1. Make sure the clinic management server is running on {server_ip}:5000")
    print("2. Double-click any shortcut to open the corresponding interface")
    print("3. Reception and Reports shortcuts work from any computer")
    print("4. Consultant shortcuts are numbered 1-5 (modify as needed)")
    
    if system == "Windows":
        print("\n🔧 Windows users: You may need to allow the shortcuts to run")

if __name__ == "__main__":
    main()
