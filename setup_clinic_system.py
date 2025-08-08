
#!/usr/bin/env python3
"""
Complete setup script for Clinic Management System
Handles both server (receptionist) and client (consultant) setup
"""
import os
import sys
import shutil
import zipfile
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess

def create_requirements_file():
    """Create requirements.txt for easier installation"""
    requirements_content = """flask>=3.1.1
flask-sqlalchemy>=3.1.1
sqlalchemy>=2.0.42
werkzeug>=3.1.3
email-validator>=2.2.0
pytz>=2025.2
"""
    return requirements_content

def create_installation_package():
    """Create complete installation package"""
    
    # Create export directory
    export_dir = "clinic_complete_system"
    if os.path.exists(export_dir):
        shutil.rmtree(export_dir)
    os.makedirs(export_dir)
    
    # Files to include for complete system
    files_to_copy = [
        'app.py',
        'main.py', 
        'models.py',
        'routes.py',
        'static/',
        'templates/',
        'instance/'  # Include the database
    ]
    
    # Copy application files
    for item in files_to_copy:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.copytree(item, os.path.join(export_dir, item))
            else:
                shutil.copy2(item, export_dir)
    
    # Create requirements.txt
    with open(os.path.join(export_dir, 'requirements.txt'), 'w') as f:
        f.write(create_requirements_file())
    
    # Copy the launcher scripts we just created
    for script in ['clinic_server_launcher.py', 'create_clinic_shortcuts.py']:
        if os.path.exists(script):
            shutil.copy2(script, export_dir)
    
    # Create comprehensive README
    readme_content = f"""# Clinic Management System - Complete Setup Guide

## Overview
This is a complete clinic management system designed for 2 laptops:
- **Receptionist's Laptop**: Runs the database server
- **Consultant's Laptop**: Connects to the server via network

## System Requirements
- Python 3.11 or higher
- Both laptops on the same WiFi network
- Windows, macOS, or Linux

## Installation Steps

### STEP 1: Install Python Dependencies (On Both Laptops)
```
pip install -r requirements.txt
```

### STEP 2: Setup Receptionist's Laptop (Database Server)

1. **Start the Server**:
   ```
   python clinic_server_launcher.py
   ```
   - This opens a control panel
   - Click "🚀 Start Server & Open Reception"
   - Note down the IP address shown (e.g., 192.168.1.100)

2. **Keep the server running** - don't close the control panel window

### STEP 3: Setup Consultant's Laptop (Client)

1. **Copy the system files** to the consultant's laptop

2. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

3. **Create desktop shortcuts**:
   ```
   python create_clinic_shortcuts.py
   ```
   - Enter the receptionist's IP address when prompted
   - Desktop shortcuts will be created automatically

4. **Use the shortcuts**:
   - Double-click "Reception - Clinic Management" for patient registration
   - Double-click "Consultant X - Clinic Management" for consultation queues
   - Double-click "Reports - Clinic Management" for generating reports

## Network Setup

### Finding IP Address:
- **Windows**: Open Command Prompt → type `ipconfig`
- **Mac/Linux**: Open Terminal → type `ifconfig` or `ip addr`
- Look for address starting with 192.168.x.x

### Firewall Settings:
- If connection fails, temporarily disable firewall to test
- Add exception for port 5000 if needed

## Usage Workflows

### Reception Workflow:
1. Start server using `python clinic_server_launcher.py`
2. Use Reception interface for patient registration
3. Search existing patients by name or phone
4. Assign patients to consultants

### Consultant Workflow:
1. Use consultant desktop shortcuts
2. Select consultant from dropdown
3. View waiting patients queue
4. Mark consultations as completed
5. View shift summaries

### Reports Workflow:
1. Use Reports interface
2. Select date ranges
3. Filter by consultant
4. Download CSV reports

## Database Information
- **Location**: `instance/clinic.db` (on receptionist's laptop only)
- **Backup**: Copy this file regularly to prevent data loss
- **Network**: All other laptops connect to this central database

## Troubleshooting

**"Port 5000 already in use"**:
- Close other applications using port 5000
- Or change port in main.py (line with app.run)

**"Can't connect from other laptops"**:
- Check both laptops are on same WiFi
- Verify IP address is correct
- Temporarily disable firewall
- Ensure server laptop is running the clinic_server_launcher.py

**"Desktop shortcuts don't work"**:
- Right-click shortcut → Properties → check URL is correct
- Manually open browser and go to http://[IP]:5000/reception

**"Database errors"**:
- Check instance/clinic.db exists on server laptop
- Restart the server launcher
- Check file permissions

## System Architecture
- **Server**: Receptionist's laptop runs Flask application + SQLite database
- **Clients**: Other laptops access via web browser using desktop shortcuts
- **Network**: All communication over local WiFi (no internet required)
- **Data**: Centralized database on receptionist's laptop

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Support
For issues, check that:
1. Python dependencies are installed on both laptops
2. Server is running on receptionist's laptop
3. Both laptops are on same network
4. Firewall allows port 5000
"""
    
    with open(os.path.join(export_dir, 'SETUP_README.md'), 'w') as f:
        f.write(readme_content)
    
    # Create quick start batch files
    # Windows batch file for server
    server_batch = """@echo off
echo Starting Clinic Management Server...
echo.
echo This will open the server control panel.
echo Keep this window open while the system is running.
echo.
python clinic_server_launcher.py
pause
"""
    
    with open(os.path.join(export_dir, 'START_SERVER.bat'), 'w') as f:
        f.write(server_batch)
    
    # Windows batch file for client setup
    client_batch = """@echo off
echo Setting up Desktop Shortcuts for Clinic Management
echo.
echo This will create desktop shortcuts for Reception, Consultants, and Reports
echo You will be asked for the server laptop's IP address
echo.
python create_clinic_shortcuts.py
pause
"""
    
    with open(os.path.join(export_dir, 'SETUP_SHORTCUTS.bat'), 'w') as f:
        f.write(client_batch)
    
    # Shell scripts for Mac/Linux
    server_shell = """#!/bin/bash
echo "Starting Clinic Management Server..."
echo
echo "This will open the server control panel."
echo "Keep this window open while the system is running."
echo
python3 clinic_server_launcher.py
"""
    
    with open(os.path.join(export_dir, 'start_server.sh'), 'w') as f:
        f.write(server_shell)
    os.chmod(os.path.join(export_dir, 'start_server.sh'), 0o755)
    
    client_shell = """#!/bin/bash
echo "Setting up Desktop Shortcuts for Clinic Management"
echo
echo "This will create desktop shortcuts for Reception, Consultants, and Reports"
echo "You will be asked for the server laptop's IP address"
echo
python3 create_clinic_shortcuts.py
"""
    
    with open(os.path.join(export_dir, 'setup_shortcuts.sh'), 'w') as f:
        f.write(client_shell)
    os.chmod(os.path.join(export_dir, 'setup_shortcuts.sh'), 0o755)
    
    return export_dir

def create_gui_installer():
    """Create GUI for easy setup"""
    root = tk.Tk()
    root.title("Clinic Management System - Setup")
    root.geometry("600x500")
    
    # Header
    header = tk.Label(root, text="🏥 Clinic Management System", 
                     font=("Arial", 18, "bold"), fg="blue")
    header.pack(pady=20)
    
    subtitle = tk.Label(root, text="Complete Setup & Deployment Tool", 
                       font=("Arial", 12))
    subtitle.pack(pady=5)
    
    # Instructions
    instructions = tk.Text(root, height=15, width=70, wrap=tk.WORD)
    instructions.pack(pady=20, padx=20)
    instructions.insert(tk.END, """Welcome to the Clinic Management System Setup!

This tool will create a complete package for deployment on your clinic laptops.

WHAT THIS CREATES:
✅ Complete application files
✅ Desktop shortcut creator
✅ Server launcher with GUI
✅ Installation instructions
✅ Batch files for Windows
✅ Shell scripts for Mac/Linux

DEPLOYMENT PROCESS:
1. Click "Create Installation Package" below
2. Copy the created folder to both laptops
3. On RECEPTIONIST'S laptop: Run START_SERVER.bat (Windows) or start_server.sh (Mac/Linux)
4. On CONSULTANT'S laptop: Run SETUP_SHORTCUTS.bat or setup_shortcuts.sh
5. Use the desktop shortcuts to access different interfaces

KEY FEATURES:
📋 Reception interface for patient registration
👩‍⚕️ Consultant interfaces with patient queues  
📊 Reports with date filtering and CSV export
💾 Centralized database on receptionist's laptop
🌐 Network access via desktop shortcuts
⚡ No internet required - works on local WiFi

The system will create desktop shortcuts that automatically connect to the correct server IP address.""")
    instructions.config(state=tk.DISABLED)
    
    # Buttons
    buttons_frame = tk.Frame(root)
    buttons_frame.pack(pady=20)
    
    def create_package():
        try:
            export_dir = create_installation_package()
            
            # Create zip file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            zip_filename = f"clinic_management_complete_{timestamp}.zip"
            
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root_dir, dirs, files in os.walk(export_dir):
                    for file in files:
                        file_path = os.path.join(root_dir, file)
                        arcname = os.path.relpath(file_path, export_dir)
                        zipf.write(file_path, arcname)
            
            messagebox.showinfo("Success!", 
                              f"✅ Installation package created successfully!\n\n"
                              f"📁 Folder: {export_dir}\n"
                              f"📦 Zip file: {zip_filename}\n\n"
                              f"📋 Next steps:\n"
                              f"1. Copy the folder or zip file to both laptops\n"
                              f"2. Follow the SETUP_README.md instructions\n"
                              f"3. Start with receptionist's laptop first")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create package:\n{str(e)}")
    
    create_btn = tk.Button(buttons_frame, text="🚀 Create Installation Package", 
                          command=create_package, bg="green", fg="white", 
                          font=("Arial", 12, "bold"), padx=30, pady=15)
    create_btn.pack()
    
    # Footer
    footer = tk.Label(root, text="This will create everything needed for deployment", 
                     font=("Arial", 9), fg="gray")
    footer.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    create_gui_installer()
