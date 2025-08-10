
@echo off
cd /d "%~dp0"
echo ========================================
echo STARTING CLINIC - RECEPTIONIST SYSTEM
echo ========================================
echo.
echo Server starting on: http://192.168.1.11:5000
echo Local access: http://localhost:5000
echo.
echo Opening browser in 5 seconds...
timeout /t 5 /nobreak >nul
start "" "http://localhost:5000"
echo.
echo Starting Flask server...
python main.py
pause
