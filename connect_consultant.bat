@echo off
echo ==========================================
echo   THE KIDS CLINIC - CONSULTANT VIEW
echo ==========================================
echo.
echo Connecting to receptionist computer...
echo Server IP: 192.168.1.2:5000
echo.
echo Testing connection...
ping -n 2 192.168.1.2 > nul
if %errorlevel% == 0 (
    echo Connection successful!
    echo Opening consultant view in 3 seconds...
    timeout /t 3
    start "" "http://192.168.1.2:5000/consultant"
) else (
    echo ERROR: Cannot connect to receptionist computer!
    echo Please ensure:
    echo 1. Receptionist computer is turned on
    echo 2. Receptionist has started the server
    echo 3. Both computers are on same network
    echo 4. Server IP is 192.168.1.2
    pause
)
echo.
echo Consultant interface is now open.
echo This window can be closed.
pause