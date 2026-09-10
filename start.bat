@echo off
setlocal enabledelayedexpansion

:: ==================================================================
:: STAGE 1 - relocate before doing anything.
::
:: cmd.exe reads a .bat file from disk line by line, remembering only a
:: byte offset. "git reset --hard" replacing this file mid-run therefore
:: makes cmd resume at that offset inside the NEW file and execute
:: whatever text happens to sit there - which is what printed
::   'delete' is not recognized as an internal or external command
:: and ran the update twice.
::
:: So: copy ourselves to %TEMP% and do all the real work from there. The
:: executing file then lives outside the repo, where git cannot touch it.
:: This stage runs no git commands, so nothing can swap the file while
:: these lines are being read. %1 carries the clinic folder to the copy.
:: ==================================================================
if "%~1"=="" (
    if not exist "%TEMP%\kidsclinic-boot" mkdir "%TEMP%\kidsclinic-boot" 2>nul
    copy /Y "%~f0" "%TEMP%\kidsclinic-boot\start.bat" >nul 2>&1
    if exist "%TEMP%\kidsclinic-boot\start.bat" (
        "%TEMP%\kidsclinic-boot\start.bat" "%~dp0." & exit /b
    )
    echo [warning] Could not stage to TEMP - running in place.
    echo.
)

:: ==================================================================
:: STAGE 2 - the real work, running from the TEMP copy.
:: "%~dp0." keeps a trailing "." so the quoted path never ends in a
:: backslash, which would escape the closing quote.
:: ==================================================================
if not "%~1"=="" cd /d "%~1"
title Kids Clinic Server

:: --- Back up the live database BEFORE any git command ---------------
:: Order matters: an update can remove clinic.db, and a backup taken
:: afterwards would capture the damage over the last good copy.
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
    ) else (
        echo OneDrive not set up - local backup only ^(backups\clinic_last_good.db^).
    )
    echo.
)

:: --- Update the code, if this folder is a git checkout ---------------
git rev-parse --git-dir >nul 2>&1
if not errorlevel 1 (
    echo Checking for updates...
    git fetch origin
    git reset --hard origin/main
    echo.
)

:: --- Put the database back if the update removed it ------------------
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
