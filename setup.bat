@echo off
REM filepath: /c:/Users/rob3r/OneDrive/Desktop/virtual_dj/setup.bat
echo === Virtual DJ Setup ===

REM Step 1: Create required directories
if not exist AudioSource mkdir AudioSource
if not exist "D:\Projects\99_Export\02_Video\01_Horizontal" mkdir "D:\Projects\99_Export\02_Video\01_Horizontal"

REM Step 2: Check for audio files with recursive search
python -c "import os; files=sum([[os.path.join(r,f) for f in fs if f.lower().endswith(('.mp3','.wav'))] for r,_,fs in os.walk('AudioSource')], []); print(f'Found {len(files)} audio files'); exit(0 if files else 1)"
if errorlevel 1 (
    echo.
    echo [ERROR] No audio files found in AudioSource directory!
    REM Open the AudioSource folder for the user
    start "" "%~dp0AudioSource"
    pause
    exit /b 1
)

REM Step 3: Install Python dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

REM Step 4: Verify FFmpeg installation
where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo FFmpeg not found! Please install from:
    echo https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z
    pause
    exit /b 1
)

REM Step 5: Check for VB-Audio Cable
powershell -Command "& {$devices = Get-WmiObject Win32_SoundDevice; if ($devices | Where-Object {$_.Name -like '*Virtual Cable*'}) {exit 0} else {exit 1}}"
if errorlevel 1 (
    echo VB-Audio Cable not found! Please install from:
    echo https://vb-audio.com/Cable/
    pause
    exit /b 1
)

echo Setup completed successfully!
pause