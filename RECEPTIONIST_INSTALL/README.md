
# RECEPTIONIST LAPTOP INSTALLATION

## Quick Installation Steps

1. **Extract this folder** to `C:\ClinicApp\RECEPTIONIST_INSTALL\`

2. **Right-click on `install.bat`** and select **"Run as administrator"**

3. **Follow the prompts** - the installer will:
   - Check Python installation
   - Install required packages
   - Setup the database
   - Create a desktop shortcut

4. **Start the system** by double-clicking the desktop shortcut **"Start Clinic - Receptionist"**

## What the installer does:
- ✓ Installs Flask, SQLAlchemy, and Gunicorn
- ✓ Creates clinic database with default consultants
- ✓ Creates desktop shortcut for easy startup
- ✓ Configures server to run on all network interfaces

## Daily Usage:
1. Double-click **"Start Clinic - Receptionist"** on desktop
2. Browser opens automatically to the receptionist interface
3. System is ready for patient registration and queue management

## Your IP Address:
After installation, note your computer's IP address:
- Press `Windows + R`, type `cmd`, press Enter
- Type `ipconfig` and press Enter
- Look for "IPv4 Address" (example: 192.168.1.100)
- Give this IP to the consultant laptop for setup

## Troubleshooting:
- If Python is missing: Download from python.org
- If shortcut doesn't work: Run `start_clinic.bat` directly
- If browser doesn't open: Manually go to http://localhost:5000
