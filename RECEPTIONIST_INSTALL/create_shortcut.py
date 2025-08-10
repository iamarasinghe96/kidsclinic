
import os
import winshell
from win32com.client import Dispatch

def create_receptionist_shortcut():
    desktop = winshell.desktop()
    path = os.path.join(desktop, "Start Clinic - Receptionist.lnk")
    target = os.path.join(os.getcwd(), "start_clinic.bat")
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = os.getcwd()
    shortcut.IconLocation = target
    shortcut.save()
    
    print(f"Desktop shortcut created: {path}")

if __name__ == "__main__":
    create_receptionist_shortcut()
