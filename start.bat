@echo off
title Kids Clinic Server

:: Check for updates (only if this is a git repository)
git rev-parse --git-dir >nul 2>&1
if not errorlevel 1 (
    echo Checking for updates...
    git fetch origin
    git reset --hard origin/main
    echo.
)

:: Back up database to OneDrive (once per day)
set BACKUP_DIR=%USERPROFILE%\OneDrive\KidsClinicBackup
if exist "%USERPROFILE%\OneDrive" (
    if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
    for /f "tokens=2 delims==" %%a in ('wmic os get localdatetime /value') do set DT=%%a
    set BACKUP_FILE=%BACKUP_DIR%\clinic_%DT:~0,8%.db
    if exist clinic.db (
        if not exist "%BACKUP_FILE%" (
            copy /Y clinic.db "%BACKUP_FILE%" >nul
            echo Backup saved to OneDrive: clinic_%DT:~0,8%.db
        ) else (
            echo Backup already exists for today.
        )
    )
    echo.
)

echo Starting server...
start "" http://localhost:5000
python main.py
pause
