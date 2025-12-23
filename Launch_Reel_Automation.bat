@echo off
echo ============================================
echo     Reel Automation - AI Video Editor
echo ============================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo.
    echo Please run setup first:
    echo   1. python -m venv venv
    echo   2. venv\Scripts\activate
    echo   3. pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo.
    echo Please create .env file from .env.example
    echo and add your API keys.
    echo.
    pause
    exit /b 1
)

REM Launch GUI
echo Launching Reel Automation GUI...
echo.
python gui.py

REM Deactivate when done
deactivate

pause
