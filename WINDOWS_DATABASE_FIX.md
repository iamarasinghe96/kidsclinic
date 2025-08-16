# Windows Database Path Fix

## Issue Resolved
The database path was hardcoded for the Linux environment. Fixed to use relative path that works on Windows.

## What Was Changed
- Updated `app.py` to use relative database path
- Database file (`clinic.db`) must be in same folder as application files
- Cross-platform compatible path resolution

## Deployment Steps for Windows

1. **Create clinic folder**: `C:\ClinicApp\`

2. **Copy these files to the folder**:
   - `app.py` (updated with Windows-compatible database path)
   - `models.py`
   - `routes.py` 
   - `clinic.db` (your patient database)
   - `test_windows_server.py` (Windows server launcher)
   - `start_clinic_simple.bat` (startup script)
   - `templates/` folder (all HTML files)
   - `static/` folder (CSS/JS files)

3. **Install packages**:
   ```cmd
   pip install flask flask-sqlalchemy werkzeug
   ```

4. **Start the system**:
   ```cmd
   cd C:\ClinicApp
   python test_windows_server.py
   ```

## File Structure Should Look Like
```
C:\ClinicApp\
├── app.py
├── models.py  
├── routes.py
├── clinic.db
├── test_windows_server.py
├── start_clinic_simple.bat
├── templates\
├── static\
└── ...other files
```

The system will now find the database file correctly on Windows!