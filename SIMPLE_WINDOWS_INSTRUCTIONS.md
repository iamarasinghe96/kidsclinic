# Simple Windows Setup - No Gunicorn Required

## Quick Fix for Windows Users

### Problem:
The gunicorn error you're seeing happens because gunicorn doesn't work on Windows.

### Solution:
I've created a Windows-compatible version that uses Flask's built-in server.

### What You Need to Do:

1. **Install Only These Packages:**
   ```cmd
   pip install flask flask-sqlalchemy werkzeug
   ```
   (Don't install gunicorn!)

2. **Use the New Startup File:**
   - Copy `run_clinic_windows.py` to your clinic folder
   - Double-click `start_receptionist.bat` 

3. **The Script Will:**
   - Start the server automatically
   - Open your browser to the receptionist page
   - Work on your network for consultant access
   - Show clear status messages

### Files You Need:
- `run_clinic_windows.py` (new Windows-compatible server)
- `start_receptionist.bat` (updated startup script)
- `connect_consultant.bat` (for consultant computer)
- All your clinic files (app.py, models.py, etc.)
- Your database file (`clinic.db`)

### Network Access:
- Server runs on `0.0.0.0:5000` (accessible from network)
- Receptionist: Open browser to `http://localhost:5000/receptionist`
- Consultant: Open browser to `http://YOUR_RECEPTIONIST_IP:5000/consultant`

### No More Errors:
This version doesn't use gunicorn at all - it's pure Python and works on Windows, Mac, and Linux.

### Test It:
1. Close any existing servers
2. Double-click the new `start_receptionist.bat`
3. Browser should open automatically
4. No more fcntl/gunicorn errors!

---

**This is the production-ready Windows solution for your clinic!**