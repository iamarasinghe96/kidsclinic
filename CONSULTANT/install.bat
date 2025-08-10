
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

REM Install required packages
echo Installing browser dependencies...
pip install winshell

echo.
echo ========================================
echo INSTALLATION COMPLETE!
echo ========================================
echo.
echo To start the consultant view: Double-click "START_CONSULTANT.bat"
echo.
pause
