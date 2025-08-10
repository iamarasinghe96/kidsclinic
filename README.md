# The Kids Clinic / Allergy and Asthma Center - Patient Management System

A local-only clinic patient management system designed for two dedicated computers with role-separated interfaces and automated startup shortcuts.

## Your System Configuration

- **Receptionist Computer**: IP Address `192.168.1.11` - Runs the web server and handles all operations
- **Consultant Computer**: IP Address `192.168.1.12` - Connects to receptionist's server for read-only viewing
- **Database**: SQLite database stored on receptionist computer
- **Printing**: Printer connected to consultant computer, shared over network

## Network Setup Verified

✅ **Receptionist Computer**: `192.168.1.11`  
✅ **Consultant Computer**: `192.168.1.12`  
✅ **Network**: Both computers on same network  
✅ **Port Required**: 5000 (will be configured in firewall)

---

## RECEPTIONIST COMPUTER SETUP (IP: 192.168.1.11)

### Step 1: Install Python (If Not Already Installed)

#### For Windows:
1. Go to https://www.python.org/downloads/
2. Download Python 3.11 or newer
3. **IMPORTANT**: Check "Add Python to PATH" during installation
4. Open Command Prompt and type `python --version` to verify

#### For Mac:
1. Open Terminal
2. Install Homebrew if not installed: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
3. Install Python: `brew install python`

#### For Linux:
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### Step 2: Download and Setup Project

1. **Create Project Folder**
   - **Windows**: Create folder `C:\ClinicApp\`
   - **Mac/Linux**: Create folder `~/ClinicApp/`

2. **Copy Project Files**
   - Extract/copy all project files into the ClinicApp folder
   - You should see files like: `app.py`, `main.py`, `models.py`, `routes.py`, etc.

### Step 3: Install Required Software

#### Windows Command Prompt (Run as Administrator):
```cmd
cd C:\ClinicApp
pip install flask flask-sqlalchemy sqlalchemy werkzeug gunicorn
```

#### Mac/Linux Terminal:
```bash
cd ~/ClinicApp
pip3 install flask flask-sqlalchemy sqlalchemy werkzeug gunicorn
```

### Step 4: Initialize Database

#### Windows:
```cmd
cd C:\ClinicApp
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database created successfully!')"
```

#### Mac/Linux:
```bash
cd ~/ClinicApp
python3 -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database created successfully!')"
```

### Step 5: Configure Windows Firewall (Windows Only)

1. Open Windows Security → Firewall & network protection
2. Click "Advanced settings"
3. Click "Inbound Rules" → "New Rule"
4. Select "Port" → Next
5. Select "TCP" → Specific local ports: `5000` → Next
6. Select "Allow the connection" → Next
7. Check all profiles → Next
8. Name: "Clinic App" → Finish

### Step 6: Create Receptionist Startup Shortcut

#### For Windows:
1. **Create Startup File**: Right-click on Desktop → New → Text Document
2. **Rename**: Change name to `Start_Receptionist.bat` (make sure it ends with .bat)
3. **Edit File**: Right-click the file → Edit, then copy and paste this content:

```batch
@echo off
cd /d "C:\ClinicApp"
echo ==========================================
echo  THE KIDS CLINIC - RECEPTIONIST SYSTEM
echo ==========================================
echo.
echo Starting server on IP: 192.168.1.11:5000
echo Local access: http://localhost:5000
echo Consultant can access: http://192.168.1.11:5000
echo.
echo Opening browser in 3 seconds...
timeout /t 3
start "" "http://localhost:5000"
echo.
echo Server is running... Do NOT close this window!
echo To stop server: Press Ctrl+C
echo.
python -m gunicorn --bind 192.168.1.11:5000 --reuse-port --reload main:app
pause
```

4. **Save and Close**
5. **Test**: Double-click the file to test it works

#### For Mac:
1. **Create Startup File**: Open TextEdit → New Document
2. **Copy Content**:
```bash
#!/bin/bash
cd ~/ClinicApp
echo "=========================================="
echo " THE KIDS CLINIC - RECEPTIONIST SYSTEM"
echo "=========================================="
echo ""
echo "Starting server on IP: 192.168.1.11:5000"
echo "Local access: http://localhost:5000"
echo "Consultant can access: http://192.168.1.11:5000"
echo ""
echo "Opening browser in 3 seconds..."
sleep 3
open "http://localhost:5000"
echo ""
echo "Server is running... Do NOT close this window!"
echo ""
python3 -m gunicorn --bind 192.168.1.11:5000 --reuse-port --reload main:app
```

3. **Save**: Save as `start_receptionist.sh` on Desktop
4. **Make Executable**: Open Terminal, type: `chmod +x ~/Desktop/start_receptionist.sh`

#### For Linux:
Same as Mac, but might need to use `python3` instead of `python`

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

## CONSULTANT COMPUTER SETUP (IP: 192.168.1.12)

### Step 1: Verify Network Connection

1. **Test Connection to Receptionist Computer**:
   - **Windows**: Open Command Prompt, type: `ping 192.168.1.11`
   - **Mac/Linux**: Open Terminal, type: `ping 192.168.1.11`
   - You should see replies confirming connection

### Step 2: Setup Printer Sharing (So Receptionist Can Print)

#### Windows Printer Sharing:
1. **Open Settings**: Windows key + I
2. **Go to Devices**: Click "Devices" → "Printers & scanners"
3. **Find Your Printer**: Click on your printer name
4. **Open Properties**: Click "Manage" → "Printer properties"
5. **Enable Sharing**: 
   - Click "Sharing" tab
   - Check "Share this printer"
   - **Write down the share name** (e.g., "HP_LaserJet")
   - Click "OK"

#### Mac Printer Sharing:
1. **Open System Preferences**: Apple menu → System Preferences
2. **Go to Sharing**: Click "Sharing"
3. **Enable Printer Sharing**:
   - Check "Printer Sharing" on the left
   - Select your printer on the right
   - **Note the printer name**

#### Linux Printer Sharing:
```bash
# Install CUPS if not installed
sudo apt install cups
# Access printer settings at: http://localhost:631
# Enable sharing in Administration section
```

### Step 3: Install/Update Web Browser
- Make sure you have Chrome, Firefox, Safari, or Edge installed
- Update to latest version

### Step 4: Create Consultant Startup Shortcut

#### For Windows:
1. **Create Startup File**: Right-click on Desktop → New → Text Document
2. **Rename**: Change name to `Start_Consultant.bat` (make sure it ends with .bat)
3. **Edit File**: Right-click the file → Edit, then copy and paste this content:

```batch
@echo off
echo ==========================================
echo   THE KIDS CLINIC - CONSULTANT VIEW
echo ==========================================
echo.
echo Connecting to receptionist computer...
echo Receptionist IP: 192.168.1.11:5000
echo.
echo Testing connection...
ping -n 2 192.168.1.11 > nul
if %errorlevel% == 0 (
    echo Connection successful!
    echo Opening consultant view in 3 seconds...
    timeout /t 3
    start "" "http://192.168.1.11:5000/consultant"
) else (
    echo ERROR: Cannot connect to receptionist computer!
    echo Please ensure:
    echo 1. Receptionist computer is turned on
    echo 2. Receptionist has started the server
    echo 3. Both computers are on same network
    pause
)
```

4. **Save and Close**

#### For Mac:
1. **Create Startup File**: Open TextEdit → New Document
2. **Copy Content**:
```bash
#!/bin/bash
echo "=========================================="
echo "  THE KIDS CLINIC - CONSULTANT VIEW"
echo "=========================================="
echo ""
echo "Connecting to receptionist computer..."
echo "Receptionist IP: 192.168.1.11:5000"
echo ""
echo "Testing connection..."
if ping -c 2 192.168.1.11 > /dev/null; then
    echo "Connection successful!"
    echo "Opening consultant view in 3 seconds..."
    sleep 3
    open "http://192.168.1.11:5000/consultant"
else
    echo "ERROR: Cannot connect to receptionist computer!"
    echo "Please ensure:"
    echo "1. Receptionist computer is turned on"
    echo "2. Receptionist has started the server"
    echo "3. Both computers are on same network"
    read -p "Press Enter to close..."
fi
```

3. **Save**: Save as `start_consultant.sh` on Desktop
4. **Make Executable**: Open Terminal, type: `chmod +x ~/Desktop/start_consultant.sh`

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

### Connect Receptionist Computer to Consultant's Printer

#### On Receptionist Computer (Windows):
1. **Open Settings**: Windows key + I
2. **Go to Printers**: Devices → Printers & scanners
3. **Add Printer**: Click "Add printer or scanner"
4. **Wait**: Let it search, then click "The printer that I want isn't listed"
5. **Select Network Printer**: Choose "Select a shared printer by name"
6. **Enter Path**: Type exactly: `\\192.168.1.12\PRINTER_SHARE_NAME`
   - Replace `PRINTER_SHARE_NAME` with the name you noted from Step 2 of consultant setup
   - Example: `\\192.168.1.12\HP_LaserJet`
7. **Install**: Follow the prompts to install drivers
8. **Test**: Print a test page to verify it works

#### On Receptionist Computer (Mac):
1. **Open System Preferences**: Apple menu → System Preferences
2. **Go to Printers**: Click "Printers & Scanners"
3. **Add Printer**: Click the "+" button
4. **Select IP Tab**: Click "IP" at the top
5. **Enter Details**:
   - **Address**: `192.168.1.12`
   - **Protocol**: Choose "Line Printer Daemon - LPD" or "Internet Printing Protocol - IPP"
   - **Queue**: Enter the printer name from consultant computer
6. **Add**: Click "Add" and install drivers if prompted

#### On Receptionist Computer (Linux):
```bash
# Open printer settings
system-config-printer
# Or use GUI: Settings → Printers
# Add → Network Printer
# Enter: smb://192.168.1.12/PRINTER_SHARE_NAME
```

---

## DAILY OPERATION GUIDE

### Starting the System (Every Day)

#### Step 1: Start Receptionist Computer First
1. **Double-click**: `Start_Receptionist.bat` (Windows) or `start_receptionist.sh` (Mac/Linux)
2. **Wait**: You'll see the server starting up
3. **Browser Opens**: Automatically opens to receptionist dashboard
4. **Keep Window Open**: Don't close the black/terminal window - that's the server!

#### Step 2: Start Consultant Computer
1. **Double-click**: `Start_Consultant.bat` (Windows) or `start_consultant.sh` (Mac/Linux)
2. **Connection Test**: Script will test connection to receptionist computer
3. **Browser Opens**: Automatically opens to consultant view
4. **Select Consultant**: Choose your name from the dropdown

### Important URLs (For Reference)

- **Receptionist Dashboard**: `http://localhost:5000` (on receptionist computer)
- **Queue Management**: `http://localhost:5000/queue_management` (on receptionist computer)
- **Consultant View**: `http://192.168.1.11:5000/consultant` (access from anywhere)
- **Reports**: `http://192.168.1.11:5000/report`
- **Admin Panel**: `http://192.168.1.11:5000/admin_login`

---

## TROUBLESHOOTING GUIDE

### Problem: Consultant Can't Connect

**Solutions to Try:**
1. **Check Network**: Both computers on same WiFi?
2. **Ping Test**: From consultant computer, type: `ping 192.168.1.11`
3. **Firewall**: Make sure port 5000 is allowed on receptionist computer
4. **Server Running**: Is the receptionist startup script still running?
5. **Restart**: Close everything and start receptionist first, then consultant

### Problem: Printer Not Working

**Solutions to Try:**
1. **Test from Consultant**: Print something directly from consultant computer first
2. **Check Sharing**: Is printer sharing enabled on consultant computer?
3. **Reinstall**: Remove and re-add the network printer on receptionist computer
4. **Drivers**: Make sure printer drivers are installed on both computers

### Problem: Website Not Loading

**Solutions to Try:**
1. **Server Status**: Check if the black/terminal window is still open on receptionist computer
2. **Restart Server**: Close the terminal window and double-click startup script again
3. **Clear Cache**: Clear browser cache (Ctrl+F5 or Cmd+Shift+R)
4. **Different Browser**: Try opening in different browser

### Problem: Database Errors

**Solutions to Try:**
1. **Restart**: Close server and restart with startup script
2. **Check File**: Make sure `clinic.db` file exists in the ClinicApp folder
3. **Recreate**: Delete `clinic.db` and run the database initialization command again

### Emergency Contact Info
- If all else fails, restart both computers and follow the daily startup steps

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

### ✅ First Time Setup (Do Once):

#### Receptionist Computer (192.168.1.11):
- [ ] Install Python 3.11+
- [ ] Create `C:\ClinicApp\` folder (Windows) or `~/ClinicApp/` (Mac/Linux)
- [ ] Copy all project files to ClinicApp folder
- [ ] Install required packages: `pip install flask flask-sqlalchemy sqlalchemy werkzeug gunicorn`
- [ ] Initialize database: Run the Python command from Step 4
- [ ] Configure Windows Firewall (Windows only)
- [ ] Create `Start_Receptionist.bat` startup file
- [ ] Test startup by double-clicking the file

#### Consultant Computer (192.168.1.12):
- [ ] Test ping to receptionist: `ping 192.168.1.11`
- [ ] Setup printer sharing (write down printer share name)
- [ ] Create `Start_Consultant.bat` startup file
- [ ] Test startup by double-clicking the file

#### Network Printer Setup:
- [ ] Add consultant's shared printer to receptionist computer
- [ ] Test printing from receptionist computer

### 📋 Daily Operation (Every Day):
1. [ ] **Start receptionist computer first**: Double-click `Start_Receptionist.bat`
2. [ ] **Wait for server to start**: Don't close the black window
3. [ ] **Start consultant computer**: Double-click `Start_Consultant.bat`
4. [ ] **Select consultant name**: Choose from dropdown on consultant screen
5. [ ] **Begin work**: Register patients, manage queue, view consultations

### 🔧 Admin Access:
- **Username**: `drajitha`
- **Password**: `ajith@galle`
- **URL**: `http://192.168.1.11:5000/admin_login`

### 💾 Backup Reminder:
- **Important**: Copy the `clinic.db` file regularly for backup
- **Location**: Inside your ClinicApp folder