
#!/usr/bin/env python3
"""
Export script to create a standalone package for desktop deployment
"""
import os
import shutil
import zipfile
from datetime import datetime

def create_desktop_export():
    # Create export directory
    export_dir = "clinic_desktop_export"
    if os.path.exists(export_dir):
        shutil.rmtree(export_dir)
    os.makedirs(export_dir)
    
    # Files and directories to include
    files_to_copy = [
        'app.py',
        'main.py', 
        'models.py',
        'routes.py',
        'pyproject.toml',
        'static/',
        'templates/',
        'instance/'  # Include the database
    ]
    
    # Copy files
    for item in files_to_copy:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.copytree(item, os.path.join(export_dir, item))
            else:
                shutil.copy2(item, export_dir)
    
    # Create requirements.txt for easier installation
    requirements_content = """flask>=3.1.1
flask-sqlalchemy>=3.1.1
sqlalchemy>=2.0.42
werkzeug>=3.1.3
email-validator>=2.2.0
pytz>=2025.2
"""
    
    with open(os.path.join(export_dir, 'requirements.txt'), 'w') as f:
        f.write(requirements_content)
    
    # Create installation and setup instructions
    readme_content = """# Clinic Management System - Desktop Installation

## Requirements
- Python 3.11 or higher
- pip (Python package installer)

## Installation Steps

1. **Install Python Dependencies**
   ```
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```
   python main.py
   ```

3. **Access the Application**
   - Open your web browser
   - Go to: http://localhost:5000
   - Or for network access: http://0.0.0.0:5000

## Network Setup (For Multiple Computers)

To use this on multiple laptops in your clinic:

1. **Find your computer's IP address:**
   - Windows: Open Command Prompt, type `ipconfig`
   - Mac/Linux: Open Terminal, type `ifconfig` or `ip addr`
   - Look for your local IP (usually starts with 192.168.x.x)

2. **Start the application** on the main computer (where you installed it)

3. **Access from other computers:**
   - Open web browser on the second laptop
   - Go to: http://[YOUR-IP-ADDRESS]:5000
   - Example: http://192.168.1.100:5000

## Database
- Your patient data is stored in `instance/clinic.db`
- This file contains all patients, consultants, and visit records
- **IMPORTANT**: Back up this file regularly to prevent data loss

## Troubleshooting

**Port already in use error:**
- Change the port in main.py from 5000 to another port (like 5001)

**Can't access from other computers:**
- Check your firewall settings
- Make sure both computers are on the same WiFi network
- Try disabling Windows Firewall temporarily to test

**Database errors:**
- Delete the `instance/clinic.db` file to reset (you'll lose all data)
- Or restore from a backup

## Usage
- **Reception Interface**: http://[IP]:5000/reception
- **Consultant Interface**: http://[IP]:5000/consultant/[consultant-id]  
- **Reports**: http://[IP]:5000/report

Generated on: {}
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    with open(os.path.join(export_dir, 'README.md'), 'w') as f:
        f.write(readme_content)
    
    # Create a simple batch file for Windows users
    batch_content = """@echo off
echo Starting Clinic Management System...
python main.py
pause
"""
    
    with open(os.path.join(export_dir, 'start_clinic.bat'), 'w') as f:
        f.write(batch_content)
    
    # Create a shell script for Mac/Linux users
    shell_content = """#!/bin/bash
echo "Starting Clinic Management System..."
python3 main.py
"""
    
    with open(os.path.join(export_dir, 'start_clinic.sh'), 'w') as f:
        f.write(shell_content)
    
    # Make shell script executable
    os.chmod(os.path.join(export_dir, 'start_clinic.sh'), 0o755)
    
    # Create zip file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_filename = f"clinic_management_desktop_{timestamp}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(export_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, export_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Desktop export created: {zip_filename}")
    print(f"📁 Export directory: {export_dir}")
    print("\n📋 Next steps:")
    print("1. Download the zip file to your desktop computer")
    print("2. Extract the zip file")
    print("3. Follow the instructions in README.md")
    print("4. Run 'pip install -r requirements.txt'")
    print("5. Run 'python main.py' to start the application")
    
    return zip_filename, export_dir

if __name__ == "__main__":
    create_desktop_export()
