REM filepath: /c:/Users/rob3r/OneDrive/Desktop/virtual_dj/start_stream.bat
@echo off
title Virtual DJ Stream
echo === Virtual DJ Startup ===

cd /d "%~dp0"

REM Check for VB-Audio Cable
echo Checking for VB-Audio Virtual Cable...
powershell -Command "& {$devices = Get-WmiObject Win32_SoundDevice; if ($devices | Where-Object {$_.Name -like '*Virtual Cable*'}) {exit 0} else {exit 1}}"
if errorlevel 1 (
    echo Error: VB-Audio Virtual Cable not found
    echo Please install VB-Audio Virtual Cable from https://vb-audio.com/Cable/
    pause
    exit /b 1
)

REM Try different Python locations
set PYTHON_STORE="%LOCALAPPDATA%\Microsoft\WindowsApps\python3.9.exe"
set PYTHON_DEFAULT="python"

echo Installing required packages...
%PYTHON_STORE% -m pip install --user psutil || %PYTHON_DEFAULT% -m pip install --user psutil

echo Starting Virtual DJ...
if exist %PYTHON_STORE% (
    echo Found Microsoft Store Python
    %PYTHON_STORE% virtual_dj.py
) else (
    echo Using default Python
    %PYTHON_DEFAULT% virtual_dj.py
)

if errorlevel 1 (
    echo.
    echo Error: Script failed to run
    echo Please ensure VB-Audio Virtual Cable is properly installed and not in use
    echo Check if FFmpeg is installed and in your system PATH
)

pause