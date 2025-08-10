
@echo off
echo ========================================
echo RECEPTIONIST LAPTOP INSTALLATION
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

REM Install required packages
echo Installing clinic dependencies...
pip install flask flask-sqlalchemy gunicorn winshell

REM Setup database
echo Setting up database...
python setup_database.py

echo.
echo ========================================
echo INSTALLATION COMPLETE!
echo ========================================
echo.
echo To start the clinic system: Double-click "START_CLINIC.bat"
echo.
pause
