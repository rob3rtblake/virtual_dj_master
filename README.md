# Virtual DJ System

A complete streaming solution that includes:
- Audio streaming through Virtual Cable
- Video streaming through Virtual Camera
- Now Playing display for OBS
- Auto-playlist generation and management

## Requirements
- Python 3.9+
- FFmpeg (latest full build)
- VB-Audio Virtual Cable
- OBS Studio

## Setup
1. Run `setup.bat` to install dependencies
2. Place audio files in `AudioSource` folder
3. Place video files in `D:\Projects\99_Export\02_Video\01_Horizontal`
4. Run `start_all.bat` to begin streaming

## Components
- `virtual_dj.py`: Main audio streaming system
- `video_compliment.py`: Video streaming system
- `now_playing.py`: Display current track in OBS

## Troubleshooting
If streams don't start:
1. Check if VB-Audio Cable is set as default recording device
2. Verify FFmpeg is in system PATH
3. Run cleanup.bat and try again
4. Check OBS audio source settings