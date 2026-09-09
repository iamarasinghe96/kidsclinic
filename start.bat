@echo off
setlocal enabledelayedexpansion
title Kids Clinic Server

:: ------------------------------------------------------------------
:: 1. Back up the live database FIRST.
::    This must run before any git command. An update can replace or
::    delete clinic.db, so a backup taken afterwards would capture the
::    damaged copy and overwrite the last good one.
:: ------------------------------------------------------------------
if exist clinic.db (
    if not exist "backups" mkdir "backups"
    copy /Y clinic.db "backups\clinic_last_good.db" >nul

    for /f "tokens=2 delims==" %%a in ('wmic os get localdatetime /value') do set DT=%%a
    set TODAY=!DT:~0,8!

    if exist "%USERPROFILE%\OneDrive" (
        set BACKUP_DIR=%USERPROFILE%\OneDrive\KidsClinicBackup
        if not exist "!BACKUP_DIR!" mkdir "!BACKUP_DIR!"
        if not exist "!BACKUP_DIR!\clinic_!TODAY!.db" (
            copy /Y clinic.db "!BACKUP_DIR!\clinic_!TODAY!.db" >nul
            echo Backup saved to OneDrive: clinic_!TODAY!.db
        ) else (
            echo OneDrive backup for today already exists.
        )
    )
    echo.
)

:: ------------------------------------------------------------------
:: 2. Update the code, if this folder is a git checkout.
:: ------------------------------------------------------------------
git rev-parse --git-dir >nul 2>&1
if not errorlevel 1 (
    echo Checking for updates...
    git fetch origin
    git reset --hard origin/main
    echo.
)

:: ------------------------------------------------------------------
:: 3. Put the database back if the update removed it.
::    clinic.db used to be tracked by git, so pulling the commit that
::    untracks it makes "git reset --hard" delete the working copy.
::    This restores it automatically on that one upgrade.
:: ------------------------------------------------------------------
if not exist clinic.db (
    if exist "backups\clinic_last_good.db" (
        echo Restoring patient database...
        copy /Y "backups\clinic_last_good.db" clinic.db >nul
        echo.
    )
)

echo Starting server...
start "" http://localhost:5000
python main.py
pause
