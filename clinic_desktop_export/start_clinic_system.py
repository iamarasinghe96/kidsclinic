
#!/usr/bin/env python3
"""
Simple Clinic System Launcher
Automatically finds and starts the clinic management system
"""
import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox

def find_clinic_directory():
    """Find the directory containing the clinic management files"""
    current_dir = os.getcwd()
    
    # Check current directory
    if os.path.exists("main.py") and os.path.exists("app.py"):
        return current_dir
    
    # Check clinic_desktop_export subdirectory
    clinic_export_dir = os.path.join(current_dir, "clinic_desktop_export")
    if os.path.exists(os.path.join(clinic_export_dir, "main.py")):
        return clinic_export_dir
    
    # Check parent directory
    parent_dir = os.path.dirname(current_dir)
    if os.path.exists(os.path.join(parent_dir, "main.py")):
        return parent_dir
    
    return None

def main():
    """Main launcher function"""
    print("🏥 Clinic Management System - Launcher")
    print("=" * 40)
    
    # Find the clinic directory
    clinic_dir = find_clinic_directory()
    
    if not clinic_dir:
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror(
            "Clinic System Not Found",
            "Could not find the clinic management system files.\n\n"
            "Please ensure you have:\n"
            "• main.py\n"
            "• app.py\n"
            "• clinic_server_launcher.py\n\n"
            "in the same directory as this launcher."
        )
        return
    
    print(f"✅ Found clinic system in: {clinic_dir}")
    
    # Change to the clinic directory
    os.chdir(clinic_dir)
    
    # Start the server launcher
    try:
        print("🚀 Starting server launcher...")
        subprocess.run([sys.executable, "clinic_server_launcher.py"])
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Launch Error",
            f"Failed to start the clinic server launcher:\n\n{str(e)}"
        )

if __name__ == "__main__":
    main()
