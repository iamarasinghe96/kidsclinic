@echo off
title Kids Clinic - Consultant Installation
echo =========================================
echo  Kids Clinic - Consultant Installation
echo =========================================
echo.

set /p SERVER_IP="Enter the server IP address (ask the receptionist): "
echo.

echo Testing connection to server...
powershell -NoProfile -Command "try { Invoke-WebRequest -Uri 'http://%SERVER_IP%:5000' -UseBasicParsing -TimeoutSec 5 | Out-Null; Write-Host 'Connected successfully.' } catch { Write-Host 'ERROR: Cannot reach server at http://%SERVER_IP%:5000'; Write-Host 'Make sure the server is running and the IP is correct.'; exit 1 }"
if errorlevel 1 ( pause & exit /b 1 )
echo.

echo Available consultants:
echo.
powershell -NoProfile -Command "$list = Invoke-RestMethod -Uri 'http://%SERVER_IP%:5000/api/consultants'; $i=1; $list | ForEach-Object { Write-Host \"  $i. $($_.name)\"; $i++ }"
echo.

set /p CHOICE="Enter the number for this consultant's PC: "

:: Resolve id and name from chosen number
for /f "tokens=*" %%L in ('powershell -NoProfile -Command "$list = Invoke-RestMethod -Uri 'http://%SERVER_IP%:5000/api/consultants'; $c = $list[%CHOICE%-1]; Write-Host \"$($c.id)|$($c.name)\""') do set CONSULTANT_INFO=%%L

for /f "tokens=1,2 delims=|" %%a in ("%CONSULTANT_INFO%") do (
    set CONSULTANT_ID=%%a
    set CONSULTANT_NAME=%%b
)

if "%CONSULTANT_ID%"=="" (
    echo Invalid selection. Please re-run the installer.
    pause
    exit /b 1
)

echo.
echo Setting up shortcut for: %CONSULTANT_NAME%

set SHORTCUT=%USERPROFILE%\Desktop\Kids Clinic - %CONSULTANT_NAME%.lnk
set TARGET_URL=http://%SERVER_IP%:5000/consultant?consultant_id=%CONSULTANT_ID%

powershell -NoProfile -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT%'); $s.TargetPath='%TARGET_URL%'; $s.Description='Kids Clinic - %CONSULTANT_NAME%'; $s.Save()"

echo Desktop shortcut created: Kids Clinic - %CONSULTANT_NAME%
echo.
echo =========================================
echo  Installation complete!
echo  Use the 'Kids Clinic - %CONSULTANT_NAME%' shortcut on your Desktop.
echo =========================================
pause
