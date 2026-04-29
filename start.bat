@echo off
title Kids Clinic Server

:: ============================================================
:: HOLIDAY THEME TESTER
:: Uncomment ONE line below to force a specific theme.
:: Leave ALL lines commented out for normal (auto) behaviour.
:: ============================================================
:: SET HOLIDAY_THEME_TEST=default
:: SET HOLIDAY_THEME_TEST=poya
:: SET HOLIDAY_THEME_TEST=vesak
:: SET HOLIDAY_THEME_TEST=christmas
:: SET HOLIDAY_THEME_TEST=pongal
:: SET HOLIDAY_THEME_TEST=islamic
:: SET HOLIDAY_THEME_TEST=deepavali
:: SET HOLIDAY_THEME_TEST=new_year
:: SET HOLIDAY_THEME_TEST=independence
:: SET HOLIDAY_THEME_TEST=hindu
:: SET HOLIDAY_THEME_TEST=christian
:: SET HOLIDAY_THEME_TEST=public_holiday
:: ============================================================

echo Checking for updates...
git fetch origin
git reset --hard origin/main
echo.
echo Starting server...
start "" http://localhost:5000
python main.py
pause
