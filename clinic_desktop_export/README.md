
# Clinic Management System - Desktop Installation

## System Requirements
- Python 3.11 or higher
- Both laptops on the same WiFi network
- Windows, macOS, or Linux

## Pre-Installation Setup

### Step 1: Install Python (if not already installed)
- **Windows**: Download from https://www.python.org/downloads/
- **macOS**: Use Homebrew: `brew install python3` or download from Python.org
- **Linux**: Use your package manager: `sudo apt install python3 python3-pip`

### Step 2: Install pip (Python Package Installer)
Most Python installations include pip, but if it's missing:

**Windows:**
```
python -m ensurepip --upgrade
```
or download get-pip.py and run:
```
python get-pip.py
```

**macOS/Linux:**
```
python3 -m ensurepip --upgrade
```

### Step 3: Verify Installation
Test that Python and pip are working:
```
python --version
pip --version
```

## Installation Steps

### STEP 1: Install Python Dependencies
Open Command Prompt/Terminal in the clinic folder and run:
```
pip install -r requirements.txt
```

**If you get errors about missing packages**, install them individually:
```
pip install flask>=3.1.1
pip install flask-sqlalchemy>=3.1.1
pip install sqlalchemy>=2.0.42
pip install werkzeug>=3.1.3
pip install email-validator>=2.2.0
pip install pytz>=2025.2
pip install requests>=2.31.0
```

**For Windows users creating shortcuts**, also install:
```
pip install pywin32
pip install winshell
```

### STEP 2: Setup Receptionist's Laptop (Database Server)

1. **Start the Server Control Panel** (choose one method):
   
   **Easy Method** (recommended):
   ```
   python start_clinic_system.py
   ```
   
   **Direct Method**:
   ```
   python clinic_server_launcher.py
   ```
   - This opens a GUI control panel
   - Click "🚀 Start Server & Open Reception"
   - **Important**: Note down the IP address shown (e.g., 192.168.1.100)

2. **Keep the control panel running** - don't close this window while the system is in use

### STEP 3: Setup Consultant's Laptop (Client)

1. **Copy the entire system folder** to the consultant's laptop

2. **Install dependencies** (same as Step 1):
   ```
   pip install -r requirements.txt
   pip install pywin32 winshell
   ```

3. **Create desktop shortcuts**:
   ```
   python create_clinic_shortcuts.py
   ```
   - Enter the receptionist's IP address when prompted (from Step 2)
   - Desktop shortcuts will be created automatically

4. **Use the shortcuts**:
   - Double-click shortcuts to access different parts of the system
   - Each shortcut automatically starts the server connection and opens the browser

## What Gets Created

### Desktop Shortcuts:
- **Reception - Clinic Management**: Patient registration and management
- **Reports - Clinic Management**: Generate and view reports
- **Consultant 1-5 - Clinic Management**: Individual consultant interfaces

### Files You Need to Keep Open:
When using the system, these processes run automatically:
1. **Server** (runs automatically when you click shortcuts)
2. **Web Browser** (opens automatically)
3. **Background processes** (managed automatically)

## Network Setup

### Finding Your IP Address:
**Windows:**
1. Press Win+R, type `cmd`, press Enter
2. Type `ipconfig` and press Enter
3. Look for "IPv4 Address" under your WiFi adapter

**macOS:**
1. Open Terminal
2. Type `ifconfig` and press Enter
3. Look for "inet" under your WiFi interface

**Linux:**
1. Open Terminal
2. Type `ip addr show` or `ifconfig`
3. Look for your network interface IP

## Troubleshooting

### "Module not found" errors:
```
pip install --upgrade pip
pip install -r requirements.txt
```

### "winshell not found" (Windows only):
```
pip install pywin32 winshell
```

### "Port already in use" error:
- Close any running Python processes
- Restart your computer if needed
- Try running the launcher again

### "Can't reach this page" error:
- Make sure the server laptop is running `clinic_server_launcher.py`
- Check that both laptops are on the same WiFi network
- Verify the IP address is correct in your shortcuts

### Firewall Issues:
- Windows: Temporarily disable Windows Firewall to test
- Allow Python through the firewall when prompted

## Database Backup
- Your data is stored in `instance/clinic.db`
- **IMPORTANT**: Copy this file regularly to backup your patient data
- To restore: Replace the file with your backup

## Usage
Once everything is set up:
1. **Reception staff**: Use "Reception" shortcut for patient registration
2. **Consultants**: Use your assigned "Consultant X" shortcut
3. **Reports**: Use "Reports" shortcut to view statistics and generate reports

## Support
If you encounter issues:
1. Check that all dependencies are installed: `pip list`
2. Verify both laptops are on the same network
3. Ensure the server laptop's control panel is running
4. Try restarting both applications

Generated on: 2025-01-09
