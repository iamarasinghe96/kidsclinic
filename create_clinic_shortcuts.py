
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
    import winshell
    from win32com.client import Dispatch
    
    desktop = winshell.desktop()
    shortcut_path = os.path.join(desktop, f"{name}.lnk")
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.TargetPath = "C:\\Windows\\System32\\cmd.exe"
    shortcut.Arguments = f'/c start "" "{url}"'
    shortcut.WorkingDirectory = os.getcwd()
    shortcut.Description = f"Open {name} - Clinic Management System"
    
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
    
    # Define shortcuts to create
    shortcuts = [
        ("Reception - Clinic Management", f"{base_url}/reception"),
        ("Reports - Clinic Management", f"{base_url}/report")
    ]
    
    # Add consultant shortcuts (you can modify consultant IDs as needed)
    for i in range(1, 6):  # Assuming 5 consultants with IDs 1-5
        shortcuts.append((f"Consultant {i} - Clinic Management", f"{base_url}/consultant?consultant_id={i}"))
    
    created_shortcuts = []
    system = platform.system()
    
    try:
        for name, url in shortcuts:
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
            
            created_shortcuts.append(shortcut_path)
            print(f"✅ Created: {shortcut_path}")
    
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
