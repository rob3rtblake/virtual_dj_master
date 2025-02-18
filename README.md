# Virtual DJ System

A complete streaming solution that integrates audio streaming through Virtual Cable, video streaming through Virtual Camera, and OBS integration with now playing display.

## Quick Start
1. Run `setup.bat` to install dependencies
2. Place audio files in `AudioSource` folder
3. Place video files in `D:\Projects\99_Export\02_Video\01_Horizontal`
4. Run `start_all.bat` to begin streaming

## Requirements
- Python 3.9+
- FFmpeg (latest full build)
- VB-Audio Virtual Cable
- OBS Studio
- Python packages:
  ```bash
  pip install psutil
  ```

## Installation Guide

### 1. Install Python
1. Open Microsoft Store
2. Search for "Python 3.9" or newer
3. Click "Get" or "Install"
4. Once installed, open Command Prompt and verify:
   ```bash
   python --version
   ```

### 2. Install OBS Studio
1. Open Microsoft Store
2. Search for "OBS Studio"
3. Click "Get" or "Install"
4. Launch OBS once to complete first-time setup

### 3. Install FFmpeg
1. Download the full FFmpeg build from https://www.gyan.dev/ffmpeg/builds/
2. Extract the archive (e.g., `ffmpeg-release-full.7z`)
3. Add these paths to Windows System Environment Variables:
   ```
   C:\Program Files\ffmpeg\bin
   C:\Program Files\ffmpeg\bin\ffmpeg.exe
   C:\Program Files\ffmpeg\bin\ffplay.exe
   C:\Program Files\ffmpeg\bin\ffprobe.exe
   ```
   Steps:
   - Press Win + X, select "System"
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "System variables" find "Path"
   - Click "Edit" and "New"
   - Add each path
   - Click "OK" on all windows

### 4. Install VB-Audio Cable
1. Download VB-Cable from https://vb-audio.com/Cable/
2. Run the installer as Administrator
3. **Important**: Restart your computer
4. After restart, configure audio devices:
   - Right-click the speaker icon in taskbar
   - Select "Open Sound Settings"
   - Under "Choose your output device":
     - Select "CABLE Input (VB-Audio Virtual Cable)"
   - Under "Choose your input device":
     - Select "CABLE Output (VB-Audio Virtual Cable)"
   - Click "Sound Control Panel" on the right
   - In Playback tab:
     - Right-click "CABLE Input"
     - Select "Set as Default Device"
     - Also set as "Default Communication Device"
   - In Recording tab:
     - Right-click "CABLE Output"
     - Select "Set as Default Device"
     - Also set as "Default Communication Device"
   - Click "Apply" and "OK"

**Note**: If you don't want all system audio going through Virtual Cable:
1. Keep your speakers/headphones as default output
2. In OBS, manually select "CABLE Output" as audio source
3. The Virtual DJ will still output to CABLE Input

### 5. Verify Installation
1. Open Command Prompt and run:
   ```bash
   python --version
   ffmpeg -version
   ```
2. Open OBS Studio
3. In OBS audio settings, you should see "CABLE Output" as an audio source

## System Overview
The Virtual DJ system is a Python-based streaming solution that handles audio playback through virtual audio devices while maintaining song metadata and playlist management.

### Directory Structure

## Components
- `virtual_dj.py`: Main audio streaming system
- `video_compliment.py`: Video streaming system
- `now_playing.py`: Display current track in OBS

## Audio Sources
The system looks for audio files in these locations:
1. `AudioSource` folder (local to the application)
2. `C:\Users\rob3r\OneDrive\Documents\Soulseek Downloads\complete`

You can add or modify source locations in `config.json`.

## Troubleshooting
If streams don't start:
1. Check if VB-Audio Cable is set as default recording device
2. Verify FFmpeg is in system PATH
3. Run cleanup.bat and try again
4. Check OBS audio source settings