
@echo off
echo ========================================
echo CONSULTANT LAPTOP INSTALLATION
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed!
    echo Please install Python 3.11+ from python.org
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing pip...
    python -m ensurepip --upgrade
)

REM Install winshell if on Windows
echo Installing Windows dependencies...
pip install winshell

REM Get receptionist IP
set /p RECEPTIONIST_IP="Enter the Receptionist laptop IP address: "

REM Create shortcut with IP
echo Creating desktop shortcut...
python create_consultant_shortcut.py "%RECEPTIONIST_IP%"

echo.
echo ========================================
echo INSTALLATION COMPLETE!
echo ========================================
echo.
echo A shortcut "Start Clinic - Consultant" has been created on your desktop.
echo Double-click it to connect to the receptionist system.
echo.
pause
