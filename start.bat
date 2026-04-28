@echo off
title Kids Clinic Server
echo Checking for updates...
git fetch origin
git reset --hard origin/main
echo.
echo Starting server...
start "" http://localhost:5000
python main.py
pause
