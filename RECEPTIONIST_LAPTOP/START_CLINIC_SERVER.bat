
@echo off
title Clinic Management Server
echo.
echo =========================================
echo    CLINIC MANAGEMENT SYSTEM - SERVER
echo =========================================
echo.
echo Starting server on this laptop...
echo This will make the system available to consultant laptops.
echo.
echo IMPORTANT: Keep this window open while clinic is operating!
echo.

cd /d "%~dp0"

python main.py

echo.
echo Server has stopped. Press any key to exit...
pause >nul
