@echo off
cd /d "%~dp0"
echo ==========================================
echo  THE KIDS CLINIC - RECEPTIONIST SYSTEM
echo ==========================================
echo.
echo Starting server...
echo Local access: http://localhost:5000/receptionist
echo Network access: http://YOUR_IP:5000/consultant
echo.
echo Opening browser in 3 seconds...
timeout /t 3
start "" "http://localhost:5000/receptionist"
echo.
echo Server running... DO NOT close this window!
echo To stop: Press Ctrl+C
echo.
python test_windows_server.py
pause