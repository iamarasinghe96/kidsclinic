
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

REM Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing pip...
    python -m ensurepip --upgrade
)

REM Install winshell if on Windows
echo Installing Windows dependencies...
pip install winshell

REM Install required packages
echo Installing clinic dependencies...
pip install flask flask-sqlalchemy gunicorn

REM Setup database
echo Setting up database...
python setup_database.py

REM Create desktop shortcut
echo Creating desktop shortcut...
python create_shortcut.py

echo.
echo ========================================
echo INSTALLATION COMPLETE!
echo ========================================
echo.
echo A shortcut "Start Clinic - Receptionist" has been created on your desktop.
echo Double-click it to start the clinic system.
echo.
pause
