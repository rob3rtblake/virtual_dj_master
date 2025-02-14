@echo off
REM filepath: /c:/Users/rob3r/OneDrive/Desktop/virtual_dj/cleanup.bat
echo === Cleaning up Virtual DJ processes ===

REM Kill any running processes
taskkill /F /IM ffmpeg.exe /T 2>nul
taskkill /F /IM ffplay.exe /T 2>nul
taskkill /F /IM python.exe /T 2>nul

REM Clean up temporary files
del /F /Q now_playing.txt 2>nul
del /F /Q *.pyc 2>nul

echo Cleanup complete!
pause