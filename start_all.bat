@echo off
REM filepath: /c:/Users/rob3r/OneDrive/Desktop/virtual_dj/start_all.bat
title Virtual DJ Control Panel
echo === Starting All Services ===

REM Install dependencies
python -m pip install -r requirements.txt

REM Start the now playing display in a new window
start "Now Playing Display" cmd /c "python now_playing.py"

REM Start the video stream in a new window
start "Video Stream" cmd /c "python video_compliment.py"

REM Start the main audio stream
call start_stream.bat