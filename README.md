# The Kids Clinic / Allergy and Asthma Center - Patient Management System

A local-only clinic patient management system designed for two dedicated laptops with role-separated interfaces and automated startup shortcuts.

## System Overview

- **Receptionist Laptop**: Runs the web application server and handles all patient registration, queue management, and administrative functions
- **Consultant Laptop**: Connects to the receptionist's server for read-only patient viewing and houses the shared printer
- **Database**: SQLite database stored on receptionist laptop, accessed via local network
- **Printing**: Printer connected to consultant laptop, shared over network for receptionist access

## Network Requirements

- Both laptops connected to the same WiFi network or LAN
- Static IP addresses recommended for consistent connection
- Firewall configured to allow port 5000 communication

---

## RECEPTIONIST LAPTOP SETUP

### Initial Setup (One-time)

1. **Install Dependencies**
   ```bash
   # Install Python 3.11 if not already installed
   # Install required packages
   pip install flask flask-sqlalchemy sqlalchemy werkzeug gunicorn
   ```

2. **Download and Extract Project**
   - Extract the project folder to: `C:\ClinicApp\` (Windows) or `~/ClinicApp/` (Mac/Linux)

3. **Environment Setup**
   - Navigate to project folder in terminal/command prompt
   - Run initial setup:
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database initialized')"
   ```

4. **Find Your IP Address**
   - **Windows**: Open Command Prompt, type `ipconfig`, look for "IPv4 Address"
   - **Mac/Linux**: Open Terminal, type `ifconfig`, look for "inet" address
   - **Example**: `192.168.1.100` (note this down for consultant laptop)

### Create Receptionist Startup Shortcut

#### For Windows:
1. Create a new file: `Start_Receptionist.bat`
2. Add this content (replace `YOUR_PROJECT_PATH`):
```batch
@echo off
cd /d "C:\ClinicApp"
echo Starting The Kids Clinic - Receptionist System...
echo.
echo Server starting on: http://0.0.0.0:5000
echo Local access: http://localhost:5000
echo.
start "" "http://localhost:5000"
python -m gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
pause
```

#### For Mac/Linux:
1. Create a new file: `start_receptionist.sh`
2. Add this content (replace `YOUR_PROJECT_PATH`):
```bash
#!/bin/bash
cd ~/ClinicApp
echo "Starting The Kids Clinic - Receptionist System..."
echo ""
echo "Server starting on: http://0.0.0.0:5000"
echo "Local access: http://localhost:5000"
echo ""
open "http://localhost:5000"
python3 -m gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```
3. Make executable: `chmod +x start_receptionist.sh`

### Daily Operation (Receptionist)

1. **Start System**: Double-click the startup shortcut
2. **Access Interface**: Browser opens automatically to receptionist dashboard
3. **Main Functions**:
   - Register new patients
   - Add returning patients to queue
   - Navigate to "Queue Management" for patient workflow
   - Mark consultations complete
   - Generate reports
   - Access admin panel (login: drajitha / ajith@galle)

---

## CONSULTANT LAPTOP SETUP

### Initial Setup (One-time)

1. **Network Configuration**
   - Ensure connected to same network as receptionist laptop
   - Note the receptionist laptop's IP address (from above)

2. **Printer Sharing Setup**
   
   #### Windows Printer Sharing:
   - Go to Settings > Devices > Printers & scanners
   - Select your printer > Manage > Printer properties
   - Go to "Sharing" tab > Check "Share this printer"
   - Note the share name (e.g., "HP_Printer")
   
   #### Mac Printer Sharing:
   - Go to System Preferences > Sharing
   - Check "Printer Sharing"
   - Select printers to share
   
   #### Linux Printer Sharing:
   - Install CUPS: `sudo apt install cups`
   - Access CUPS web interface: http://localhost:631
   - Configure printer sharing in Administration

3. **Browser Setup**
   - Install/update web browser (Chrome, Firefox, Safari, Edge)
   - Bookmark the consultant URL (see below)

### Create Consultant Startup Shortcut

#### For Windows:
1. Create a new file: `Start_Consultant.bat`
2. Add this content (replace `RECEPTIONIST_IP` with actual IP):
```batch
@echo off
echo Starting The Kids Clinic - Consultant View...
echo.
echo Connecting to receptionist system...
echo Server: http://RECEPTIONIST_IP:5000
echo.
timeout /t 3
start "" "http://RECEPTIONIST_IP:5000/consultant"
```

#### For Mac/Linux:
1. Create a new file: `start_consultant.sh`
2. Add this content (replace `RECEPTIONIST_IP` with actual IP):
```bash
#!/bin/bash
echo "Starting The Kids Clinic - Consultant View..."
echo ""
echo "Connecting to receptionist system..."
echo "Server: http://RECEPTIONIST_IP:5000"
echo ""
sleep 3
open "http://RECEPTIONIST_IP:5000/consultant"
```
3. Make executable: `chmod +x start_consultant.sh`

### Daily Operation (Consultant)

1. **Start System**: Double-click the startup shortcut
2. **Select Consultant**: Choose your name from the dropdown
3. **View Patients**: Read-only display shows:
   - Current waiting patients
   - Recently completed consultations
   - Patient details when receptionist selects them
4. **Auto-Refresh**: Page updates automatically every 30 seconds

---

## NETWORK PRINTER SETUP

### On Receptionist Laptop

#### Windows:
1. Go to Settings > Devices > Printers & scanners
2. Click "Add printer or scanner"
3. Select "The printer that I want isn't listed"
4. Choose "Select a shared printer by name"
5. Enter: `\\CONSULTANT_LAPTOP_IP\PRINTER_SHARE_NAME`
6. Follow installation prompts

#### Mac:
1. Go to System Preferences > Printers & Scanners
2. Click "+" to add printer
3. Click "IP" tab
4. Enter consultant laptop's IP address
5. Select appropriate protocol and queue name

#### Linux:
1. Open printer settings
2. Add > Network Printer
3. Enter: `smb://CONSULTANT_LAPTOP_IP/PRINTER_SHARE_NAME`

---

## SYSTEM URLS

- **Receptionist Dashboard**: `http://localhost:5000` (on receptionist laptop)
- **Queue Management**: `http://localhost:5000/queue_management`
- **Consultant View**: `http://RECEPTIONIST_IP:5000/consultant` (from any device)
- **Reports**: `http://localhost:5000/report`
- **Admin Panel**: `http://localhost:5000/admin_login`

---

## TROUBLESHOOTING

### Connection Issues
- Verify both laptops on same network
- Check firewall settings (allow port 5000)
- Test connection: `ping RECEPTIONIST_IP` from consultant laptop

### Printer Issues
- Restart printer sharing service
- Verify printer drivers installed on both laptops
- Test print from consultant laptop first

### Application Issues
- Restart receptionist server (close and reopen shortcut)
- Clear browser cache and reload
- Check terminal/command prompt for error messages

### Emergency Reset
- Close all browser windows
- Stop server (Ctrl+C in terminal)
- Restart using shortcut

---

## ADMIN CREDENTIALS

- **Username**: drajitha
- **Password**: ajith@galle

---

## SUPPORT NOTES

- Database file: `clinic.db` (on receptionist laptop)
- Log files: Check terminal/command prompt output
- Backup: Copy `clinic.db` file regularly
- Updates: Replace project files and restart system

---

## QUICK START CHECKLIST

### First Time Setup:
- [ ] Install Python and dependencies on receptionist laptop
- [ ] Extract project files
- [ ] Initialize database
- [ ] Find receptionist laptop IP address
- [ ] Create startup shortcuts for both laptops
- [ ] Setup printer sharing on consultant laptop
- [ ] Add shared printer on receptionist laptop
- [ ] Test connections

### Daily Operation:
- [ ] Start receptionist system (double-click shortcut)
- [ ] Start consultant system (double-click shortcut)
- [ ] Verify printer connectivity
- [ ] Begin patient registration and consultations