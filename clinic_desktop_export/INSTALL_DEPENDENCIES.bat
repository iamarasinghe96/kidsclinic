
@echo off
title Clinic Management System - Install Dependencies
echo.
echo 🏥 Clinic Management System - Dependency Installer
echo =======================================================
echo.
echo This will install all required Python packages.
echo Make sure you have Python and pip installed first.
echo.
echo Checking Python installation...
python --version
if errorlevel 1 (
    echo.
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo.
echo Checking pip installation...
pip --version
if errorlevel 1 (
    echo.
    echo ❌ pip is not available
    echo Installing pip...
    python -m ensurepip --upgrade
)

echo.
echo Starting automatic installation...
python install_dependencies.py

echo.
echo Installation complete!
echo.
pause
