@echo off
cd /d "%~dp0"
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