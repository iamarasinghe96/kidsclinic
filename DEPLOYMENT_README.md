# The Kids Clinic / Allergy and Asthma Center - Network Deployment Guide

A complete local clinic patient management system ready for network deployment with role-separated interfaces operating offline via LAN using SQLite database.

## System Overview

This system operates on two dedicated laptops with specialized interfaces:
- **Receptionist Laptop (192.168.1.2)**: Complete patient management, registration, queue management, and administrative functions
- **Consultant Laptop (192.168.1.12)**: Read-only display showing patient information that automatically syncs with receptionist actions

## Features

### Core Functionality
- **Patient Registration**: Complete patient data with titles (Baby, Mr., Mrs., Miss, Master, Rev.), weight tracking, email addresses, and parent names
- **Queue Management**: Real-time patient queue with auto-refresh every 10 seconds
- **Visit Tracking**: Multiple visits per day support with comprehensive status management
- **Reports**: Generate consultation summaries, analytics, and CSV exports with date filtering
- **Admin Panel**: Bulk patient and consultant management with search capabilities

### Technical Features
- **Offline Operation**: Works entirely without internet connection using SQLite database
- **Network Synchronization**: Real-time updates between laptops via LAN
- **Cross-Device Printing**: Network printer sharing configuration
- **Enhanced UI**: Bootstrap dark theme with responsive design and print optimization
- **Database**: Contains 122 patients, 133 visits, and 3 active consultants

## Network Deployment Instructions

### Prerequisites
- Two Windows/Mac/Linux computers with Python 3.8+ installed
- Local network connection (LAN/WiFi)
- Network printer (optional but recommended)

### Step 1: Download and Setup Project Files

1. **Create Project Folder on Receptionist Computer:**
   - Windows: Create folder `C:\ClinicApp\`
   - Mac/Linux: Create folder `~/ClinicApp/`

2. **Copy All Project Files:**
   - Extract/copy all project files to the ClinicApp folder
   - Ensure `clinic.db` file is included (contains your patient data)
   - Files should include: `app.py`, `main.py`, `models.py`, `routes.py`, templates folder, static folder, etc.

### Step 2: Install Python Dependencies

#### On Receptionist Computer:

**Windows Command Prompt (Run as Administrator):**
```cmd
cd C:\ClinicApp
pip install flask flask-sqlalchemy werkzeug
```

**Mac/Linux Terminal:**
```bash
cd ~/ClinicApp
pip3 install flask flask-sqlalchemy werkzeug
```

### Step 3: Configure Network Settings

#### Set Static IP Addresses:
1. **Receptionist Computer**: Configure to use IP 192.168.1.2
2. **Consultant Computer**: Configure to use IP 192.168.1.12

#### Test Network Connectivity:
```cmd
# From consultant computer, test connection:
ping 192.168.1.2
```

### Step 4: Configure Firewall (Windows)

#### On Receptionist Computer:
1. Open Windows Security → Firewall & network protection
2. Click "Advanced settings"
3. Click "Inbound Rules" → "New Rule"
4. Select "Port" → Next
5. Select "TCP" → Specific local ports: `5000` → Next
6. Select "Allow the connection" → Next
7. Check all profiles → Next
8. Name: "Clinic Management System" → Finish

### Step 5: Create Startup Scripts

#### Receptionist Computer Startup Script

**Windows - Create `Start_Clinic_Server.bat`:**
```batch
@echo off
cd /d "C:\ClinicApp"
echo ==========================================
echo  THE KIDS CLINIC - RECEPTIONIST SYSTEM
echo ==========================================
echo.
echo Starting server on IP: 192.168.1.2:5000
echo Local access: http://localhost:5000/receptionist
echo Consultant access: http://192.168.1.2:5000/consultant
echo Reports: http://192.168.1.2:5000/report
echo Admin: http://192.168.1.2:5000/admin
echo.
echo Opening receptionist interface in 3 seconds...
timeout /t 3
start "" "http://localhost:5000/receptionist"
echo.
echo Server is running... Do NOT close this window!
echo To stop server: Press Ctrl+C
echo.
python -m gunicorn --bind 0.0.0.0:5000 --reload main:app
pause
```

**Mac/Linux - Create `start_clinic_server.sh`:**
```bash
#!/bin/bash
cd ~/ClinicApp
echo "=========================================="
echo " THE KIDS CLINIC - RECEPTIONIST SYSTEM"
echo "=========================================="
echo ""
echo "Starting server on IP: 192.168.1.2:5000"
echo "Local access: http://localhost:5000/receptionist"
echo "Consultant access: http://192.168.1.2:5000/consultant"
echo "Reports: http://192.168.1.2:5000/report"
echo "Admin: http://192.168.1.2:5000/admin"
echo ""
echo "Opening receptionist interface in 3 seconds..."
sleep 3
open "http://localhost:5000/receptionist"
echo ""
echo "Server is running... Do NOT close this window!"
echo ""
python3 -m gunicorn --bind 0.0.0.0:5000 --reload main:app
```

#### Consultant Computer Access Script

**Windows - Create `Connect_To_Clinic.bat`:**
```batch
@echo off
echo ==========================================
echo   THE KIDS CLINIC - CONSULTANT VIEW
echo ==========================================
echo.
echo Connecting to receptionist computer...
echo Server IP: 192.168.1.2:5000
echo.
echo Testing connection...
ping -n 2 192.168.1.2 > nul
if %errorlevel% == 0 (
    echo Connection successful!
    echo Opening consultant view in 3 seconds...
    timeout /t 3
    start "" "http://192.168.1.2:5000/consultant"
) else (
    echo ERROR: Cannot connect to receptionist computer!
    echo Please ensure:
    echo 1. Receptionist computer is turned on
    echo 2. Receptionist has started the server
    echo 3. Both computers are on same network
    echo 4. Server IP is 192.168.1.2
    pause
)
```

**Mac/Linux - Create `connect_to_clinic.sh`:**
```bash
#!/bin/bash
echo "=========================================="
echo "  THE KIDS CLINIC - CONSULTANT VIEW"
echo "=========================================="
echo ""
echo "Connecting to receptionist computer..."
echo "Server IP: 192.168.1.2:5000"
echo ""
echo "Testing connection..."
if ping -c 2 192.168.1.2 > /dev/null; then
    echo "Connection successful!"
    echo "Opening consultant view in 3 seconds..."
    sleep 3
    open "http://192.168.1.2:5000/consultant"
else
    echo "ERROR: Cannot connect to receptionist computer!"
    echo "Please ensure:"
    echo "1. Receptionist computer is turned on"
    echo "2. Receptionist has started the server"
    echo "3. Both computers are on same network"
    echo "4. Server IP is 192.168.1.2"
    read -p "Press Enter to close..."
fi
```

### Step 6: Daily Operation

#### Starting the System:

1. **On Receptionist Computer:**
   - Double-click `Start_Clinic_Server.bat` (Windows) or `start_clinic_server.sh` (Mac/Linux)
   - Wait for the server to start (browser will open automatically)
   - Keep the terminal/command window open (this is the server)

2. **On Consultant Computer:**
   - Double-click `Connect_To_Clinic.bat` (Windows) or `connect_to_clinic.sh` (Mac/Linux)
   - Browser will open to consultant interface
   - Select your consultant name from the dropdown

### Step 7: System Access Points

#### Main URLs:
- **Receptionist Dashboard**: `http://192.168.1.2:5000/receptionist`
- **Consultant Interface**: `http://192.168.1.2:5000/consultant`
- **Queue Management**: `http://192.168.1.2:5000/queue_management`
- **Reports**: `http://192.168.1.2:5000/report`
- **Admin Panel**: `http://192.168.1.2:5000/admin`

#### Admin Access:
- **Username**: `drajitha`
- **Password**: `ajith@galle`

### System Information

#### Current Database Content:
- **Patients**: 122 registered patients with complete data
- **Visits**: 133 visit records (August 8-16, 2025)
- **Consultants**: 
  - Dr. Ajith Amarasinghe (ID: 1)
  - Dr. K.A.I.U. Imbulana (ID: 2)
  - Mr. J.M. Fernando (ID: 3)

#### Features Available:
- Patient registration with title dropdown (Baby, Mr., Mrs., Miss, Master, Rev.)
- Weight tracking per visit
- Email addresses and parent names
- Real-time queue management with auto-refresh
- Comprehensive reporting with date filtering
- Print-optimized patient summaries
- Cross-device synchronization

### Troubleshooting

#### Common Issues:

1. **Consultant can't connect:**
   - Check if receptionist server is running
   - Verify network connectivity: `ping 192.168.1.2`
   - Check firewall settings on receptionist computer
   - Ensure both computers on same network

2. **Reports showing no data:**
   - Use date range: August 8-16, 2025 for existing data
   - Check that you're connected to correct database

3. **Server won't start:**
   - Check if port 5000 is already in use
   - Restart computer and try again
   - Verify Python and packages are installed correctly

4. **Database errors:**
   - Ensure `clinic.db` file exists in project folder
   - Check file permissions
   - Restart the server

#### Emergency Steps:
1. Close all applications
2. Restart both computers
3. Start receptionist server first
4. Wait 30 seconds, then start consultant connection

### Backup Instructions

#### Regular Backup (Recommended Weekly):
1. Copy the entire `ClinicApp` folder to external drive
2. Special attention to `clinic.db` file (contains all patient data)
3. Store backup in secure location

#### Quick Backup (Daily):
1. Copy just the `clinic.db` file
2. Rename with date: `clinic_backup_YYYYMMDD.db`

### Support Contact

For technical issues or system modifications, contact your IT support team with this deployment guide.

---

## Quick Start Checklist

### ✅ One-Time Setup:

#### Receptionist Computer (192.168.1.2):
- [ ] Install Python 3.8+
- [ ] Create ClinicApp folder and copy all project files
- [ ] Install packages: `pip install flask flask-sqlalchemy gunicorn werkzeug`
- [ ] Configure firewall to allow port 5000
- [ ] Create and test startup script
- [ ] Verify database file (`clinic.db`) is present

#### Consultant Computer (192.168.1.12):
- [ ] Test network connection: `ping 192.168.1.2`
- [ ] Create and test connection script
- [ ] Configure any printer sharing if needed

### 📋 Daily Operation:
1. [ ] Start receptionist computer server first
2. [ ] Wait for browser to open automatically
3. [ ] Start consultant computer connection
4. [ ] Select consultant name from dropdown
5. [ ] Begin patient management and consultations

### 🔒 Security Notes:
- System operates offline only (no internet access required)
- Admin panel is password protected
- Database file should be backed up regularly
- Keep both computers on secure local network only

This system is now ready for production use in your clinic environment!