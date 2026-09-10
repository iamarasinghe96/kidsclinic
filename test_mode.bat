@echo off
title Kids Clinic - TEST MODE (not the real server)

:: This is a preview/testing launcher, separate from start.bat.
:: It does NOT update code, does NOT touch OneDrive, and does NOT run git.
:: Close this window and use start.bat for the real clinic day.

echo =========================================
echo  Kids Clinic - TEST MODE
echo  (holiday themes + weekly backup popup)
echo =========================================
echo.
echo Holiday theme to preview:
echo   0.  No override - show today's real theme
echo   1.  Christmas
echo   2.  Poya (Full Moon)
echo   3.  Vesak
echo   4.  Pongal
echo   5.  Islamic (Eid)
echo   6.  Deepavali
echo   7.  Sinhala / Tamil New Year
echo   8.  Independence Day
echo   9.  Hindu (Maha Sivarathri)
echo   10. Christian (Good Friday)
echo   11. Generic public holiday
echo.
set /p THEME_CHOICE="Enter a number (0-11): "

if "%THEME_CHOICE%"=="1"  set HOLIDAY_THEME_TEST=christmas
if "%THEME_CHOICE%"=="2"  set HOLIDAY_THEME_TEST=poya
if "%THEME_CHOICE%"=="3"  set HOLIDAY_THEME_TEST=vesak
if "%THEME_CHOICE%"=="4"  set HOLIDAY_THEME_TEST=pongal
if "%THEME_CHOICE%"=="5"  set HOLIDAY_THEME_TEST=islamic
if "%THEME_CHOICE%"=="6"  set HOLIDAY_THEME_TEST=deepavali
if "%THEME_CHOICE%"=="7"  set HOLIDAY_THEME_TEST=new_year
if "%THEME_CHOICE%"=="8"  set HOLIDAY_THEME_TEST=independence
if "%THEME_CHOICE%"=="9"  set HOLIDAY_THEME_TEST=hindu
if "%THEME_CHOICE%"=="10" set HOLIDAY_THEME_TEST=christian
if "%THEME_CHOICE%"=="11" set HOLIDAY_THEME_TEST=public_holiday

echo.
set /p BACKUP_CHOICE="Also force-show the weekly Google Drive backup popup on every page load? (y/n): "
if /i "%BACKUP_CHOICE%"=="y" set MONDAY_BACKUP_TEST=1

echo.
echo =========================================
if defined HOLIDAY_THEME_TEST (
    echo  Holiday theme forced to: %HOLIDAY_THEME_TEST%
) else (
    echo  Holiday theme: today's real theme ^(no override^)
)
if defined MONDAY_BACKUP_TEST (
    echo  Weekly backup popup: ON every page load
) else (
    echo  Weekly backup popup: normal behaviour ^(Mondays only^)
)
echo =========================================
echo.
echo Starting server in TEST MODE...
echo Close this window when finished testing.
echo.
start "" http://localhost:5000
python main.py
pause
