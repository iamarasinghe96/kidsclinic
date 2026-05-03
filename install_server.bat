@echo off
title Kids Clinic - Server Installation
echo =========================================
echo  Kids Clinic - Server Installation
echo =========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Opening download page...
    start "" https://www.python.org/downloads/
    echo Please install Python 3.11+ then re-run this installer.
    pause
    exit /b 1
)
echo Python found.
echo.

echo Installing Python dependencies...
pip install flask flask-sqlalchemy pytz werkzeug sqlalchemy >nul 2>&1
if errorlevel 1 (
    echo Dependency installation failed. Please check your internet connection.
    pause
    exit /b 1
)
echo Dependencies installed.
echo.

:: Create desktop shortcut to start.bat
set INSTALL_DIR=%~dp0
set SHORTCUT=%USERPROFILE%\Desktop\Kids Clinic.lnk
powershell -NoProfile -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT%'); $s.TargetPath='%INSTALL_DIR%start.bat'; $s.WorkingDirectory='%INSTALL_DIR%'; $s.Description='Kids Clinic Server'; $s.Save()"
echo Desktop shortcut created: Kids Clinic
echo.

echo =========================================
echo  Server IP address (share with consultant PCs):
powershell -NoProfile -Command "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notmatch 'Loopback' -and $_.IPAddress -notmatch '^169' } | Select-Object -First 1).IPAddress"
echo =========================================
echo.
echo Installation complete!
echo Use the 'Kids Clinic' shortcut on your Desktop to start the server.
pause
