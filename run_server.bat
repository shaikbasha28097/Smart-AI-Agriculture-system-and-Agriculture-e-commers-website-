@echo off
title Smart AI Agriculture Ecosystem Server
color 0A
cd /d "%~dp0"

echo ======================================================================
echo           SMART AI AGRICULTURE ECOSYSTEM SERVER LAUNCHER
echo ======================================================================
echo.
echo Checking Python installation...
python --version
if errorlevel 1 (
    echo [ERROR] Python is not found in PATH! Please install Python 3.9+.
    pause
    exit /b
)

echo.
echo Starting Flask Server on http://127.0.0.1:5000 ...
echo Press CTRL+C to stop the server at any time.
echo.

start "" "http://127.0.0.1:5000/"

python app.py
pause

