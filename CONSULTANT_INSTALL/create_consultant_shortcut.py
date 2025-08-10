
import os
import sys
import winshell
from win32com.client import Dispatch

def create_consultant_shortcut(receptionist_ip):
    desktop = winshell.desktop()
    path = os.path.join(desktop, "Start Clinic - Consultant.lnk")
    target = os.path.join(os.getcwd(), "start_consultant.bat")
    
    # Create the batch file with the IP
    with open("start_consultant.bat", "w") as f:
        f.write(f'''@echo off
echo ========================================
echo STARTING CLINIC - CONSULTANT VIEW
echo ========================================
echo.
echo Connecting to receptionist system...
echo Server: http://{receptionist_ip}:5000
echo.
timeout /t 3
start "" "http://{receptionist_ip}:5000/consultant"
''')
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = os.getcwd()
    shortcut.IconLocation = target
    shortcut.save()
    
    print(f"Desktop shortcut created: {path}")
    print(f"Configured for receptionist IP: {receptionist_ip}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        receptionist_ip = sys.argv[1]
    else:
        receptionist_ip = input("Enter the Receptionist laptop IP address: ")
    
    create_consultant_shortcut(receptionist_ip)
