# Virtual DJ System

Automated music streaming system with OBS integration and watchdog monitoring.

## Features
- Automatic playlist generation and management
- OBS integration with Now Playing display
- Watchdog monitoring for stability
- Virtual audio device support
- Automatic crash recovery

## Quick Start
1. Run `setup.bat` to install dependencies
2. Add music to `AudioSource` folder
3. Configure `config.json` with your settings
4. Run `start_stream.bat` to begin

## Requirements
- Python 3.9+
- FFmpeg (latest)
- VB-Audio Virtual Cable
- OBS Studio 29+
- Windows 10/11

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

## Directory Structure
```
virtual_dj_master/
├── AudioSource/       # Music library
├── logs/             # Application logs
├── config.json       # Configuration
├── setup.bat         # Installation script
├── start_stream.bat  # Launch script
├── cleanup.bat       # Process cleanup
└── *.py             # Python source files
```

## Configuration
Edit `config.json` to customize:
```json
{
    "audio_sources": ["AudioSource"],
    "obs": {
        "scene_name": "Your Scene Name",
        "profile_name": "Your Profile"
    },
    "watchdog": {
        "timeout_seconds": 10,
        "max_skips": 3
    }
}
```

## Troubleshooting
1. Audio issues:
   - Verify Virtual Cable installation
   - Check Windows audio settings
   - Run cleanup.bat before restart

2. OBS issues:
   - Check OBS installation path
   - Verify scene and profile names
   - Enable WebSocket server

3. Playback issues:
   - Check file permissions
   - Verify audio file formats
   - Check log files in logs/

## Support
- Report issues on GitHub
- Check DOCUMENTATION.md for technical details
- Run setup.bat for dependency verification

## License
GNU General Public License v3.0