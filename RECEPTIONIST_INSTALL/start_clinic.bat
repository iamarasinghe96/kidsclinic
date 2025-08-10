
@echo off
cd /d "%~dp0"
echo ========================================
echo STARTING CLINIC - RECEPTIONIST SYSTEM
echo ========================================
echo.
echo Server starting on: http://0.0.0.0:5000
echo Local access: http://localhost:5000
echo.
echo Opening browser in 3 seconds...
timeout /t 3 /nobreak >nul
start "" "http://localhost:5000"
python -c "
import subprocess
import sys
try:
    subprocess.run([sys.executable, '-m', 'gunicorn', '--bind', '0.0.0.0:5000', '--reload', 'main:app'], check=True)
except KeyboardInterrupt:
    print('Clinic system stopped.')
except Exception as e:
    print(f'Error: {e}')
    input('Press Enter to close...')
"
