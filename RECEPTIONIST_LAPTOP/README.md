
# Receptionist Laptop Setup

## What This Folder Contains
This is the complete clinic management system for the **RECEPTIONIST'S LAPTOP** (the main server).

## Installation Steps

### Step 1: Install Python Dependencies
Open Command Prompt in this folder and run:
```
pip install flask flask-sqlalchemy sqlalchemy werkzeug email-validator pytz requests
pip install pywin32 winshell
```

### Step 2: Start the Clinic System
Double-click: `START_CLINIC_SERVER.bat`

Or manually run:
```
python main.py
```

### Step 3: Note Your IP Address
The system will show your IP address (e.g., 192.168.1.100). 
**Write this down** - the consultant laptop will need it.

## What This Does
- Starts the database server
- Opens the Reception interface automatically
- Makes the system available to other laptops on your network
- Stores all patient data in this laptop

## Keep Running
Keep the server window open while the clinic is operating.

## Access Points
- Reception: http://localhost:5000/reception
- Reports: http://localhost:5000/report
- Admin: http://localhost:5000/admin
