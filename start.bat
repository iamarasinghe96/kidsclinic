@echo off
title Kids Clinic Server
echo Checking for updates...
git pull
echo.
echo Starting server...
start "" http://localhost:5000
python main.py
pause
