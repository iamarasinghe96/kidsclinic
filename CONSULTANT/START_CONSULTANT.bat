
@echo off
echo ========================================
echo STARTING CLINIC - CONSULTANT VIEW
echo ========================================
echo.
echo Connecting to receptionist system...
echo Server: http://192.168.1.11:5000
echo.
echo Opening browser in 3 seconds...
timeout /t 3 /nobreak >nul
start "" "http://192.168.1.11:5000/consultant"
echo.
echo Consultant view opened in browser.
echo You can close this window.
echo.
pause
