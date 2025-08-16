# Windows Compatibility Fix

## Issue Resolved: Gunicorn Not Working on Windows

The original deployment instructions included `gunicorn` which doesn't work on Windows due to missing `fcntl` module. This has been fixed.

### What Was Changed:
1. **Removed gunicorn dependency** - Windows doesn't support it
2. **Updated startup scripts** - Now use Flask's built-in development server
3. **Fixed main.py** - Configured for network access with host='0.0.0.0'

### Correct Installation Commands:

#### Windows:
```cmd
pip install flask flask-sqlalchemy werkzeug
```

#### Mac/Linux:
```bash
pip3 install flask flask-sqlalchemy werkzeug
```

### Startup Scripts Now Use:
- **Windows**: `python main.py` 
- **Mac/Linux**: `python3 main.py`

### Network Configuration Confirmed:
- **Host**: 0.0.0.0 (allows network access)
- **Port**: 5000
- **Debug**: False (production mode)

### Ready to Deploy:
Your system is now fully Windows-compatible and ready for deployment on your clinic network. Simply follow the DEPLOYMENT_README.md instructions with the corrected package installation commands.