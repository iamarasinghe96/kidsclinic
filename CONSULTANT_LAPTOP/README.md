
# Consultant Laptop Setup

## What This Folder Contains
This is the consultant interface that connects to the receptionist's laptop.

## Installation Steps

### Step 1: Install Python Dependencies
Open Command Prompt in this folder and run:
```
pip install flask flask-sqlalchemy sqlalchemy werkzeug email-validator pytz requests
pip install pywin32 winshell
```

### Step 2: Get Receptionist's IP Address
Ask the receptionist for their laptop's IP address (shown when they started their server).

### Step 3: Create Desktop Shortcuts
Double-click: `SETUP_SHORTCUTS.bat`

When prompted, enter the receptionist's IP address (e.g., 192.168.1.100).

### Step 4: Use the Shortcuts
Desktop shortcuts will be created:
- **Reception - Clinic Management** (for backup access)
- **Consultant 1 - Clinic Management** (consultant queue)
- **Consultant 2 - Clinic Management** (consultant queue)
- **Reports - Clinic Management** (view reports)

## How It Works
- Clicking shortcuts automatically connects to the receptionist's server
- No need to start anything manually
- All data is stored on the receptionist's laptop

## Troubleshooting
- Make sure both laptops are on the same WiFi
- Verify the IP address is correct
- Check that the receptionist's server is running
