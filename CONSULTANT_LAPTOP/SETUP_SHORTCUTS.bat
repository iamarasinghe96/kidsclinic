
@echo off
title Setup Clinic Shortcuts
echo.
echo =========================================
echo    CLINIC SHORTCUTS SETUP
echo =========================================
echo.
echo This will create desktop shortcuts to access the clinic system.
echo.

cd /d "%~dp0"

python create_clinic_shortcuts.py

echo.
echo Setup complete! Press any key to exit...
pause >nul
