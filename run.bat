@echo off
title Spendly — Local Server
cd /d "%~dp0"

echo.
echo  ====================================================
echo   SPENDLY  ^|  Personal Finance Tracker
echo   http://localhost:5001
echo  ====================================================
echo.

REM Check Python
where python >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python not found. Install Python 3.9+ and try again.
    pause & exit /b 1
)

REM Try activating venv if it exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Install requirements if missing
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo  Installing dependencies...
    pip install -r requirements.txt --quiet
)

REM Init DB if not exists
if not exist "database\spendly.db" (
    echo  Initializing database...
    python init_db.py
)

echo  Opening browser in 3 seconds...
start /min cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:5001"

echo  Starting server at http://localhost:5001
echo  Press Ctrl+C to stop.
echo.

python run.py

pause
