@echo off
cd /d "%~dp0"
echo Drag and Drop your video file here:
set /p VIDEO_PATH=
set VIDEO_PATH=%VIDEO_PATH:"=%

if not exist "%VIDEO_PATH%" (
    echo File not found!
    pause
    exit /b 1
)

python transcribe.py "%VIDEO_PATH%"
start "" "%VIDEO_PATH%.transcript.txt"
pause
