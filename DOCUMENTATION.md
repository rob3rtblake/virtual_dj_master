# Virtual DJ System - Technical Documentation

## System Overview
The Virtual DJ system is a Python-based streaming solution that handles audio playback through virtual audio devices while maintaining song metadata and playlist management.

## Key Components

### 1. Audio Pipeline
```
Audio Files -> FFmpeg -> Virtual Cable -> OBS
```
- **Solution**: Simplified FFmpeg command chain to reduce audio artifacts
- **Fixed Issues**: 
  - Removed double-pipe that caused static
  - Added proper audio buffering
  - Normalized sample rates

### 2. Song Detection
```python
# Method evolved from:
if "Opening" in line:
    file_path = line.split()[1]  # Original basic detection

# To current solution:
if "Opening '" in line:
    file_path = line.split("'")[1]
    parts = os.path.relpath(file_path, AUDIO_SOURCE).split(os.sep)
    artist = parts[0]
    album = parts[1]
    title = os.path.splitext(parts[-1])[0]
```

### 3. Solved Issues

1. **Audio Quality**
   - Problem: Static and crackling
   - Solution: Removed mutagen real-time reading
   - Result: Clean audio output

2. **Song Metadata**
   - Problem: Missing artist/title info
   - Solution: Parse from folder structure
   - Format: `AudioSource/Artist/Album/XX - Title.mp3`

3. **File Management**
   - Problem: Git tracking audio files
   - Solution: Added .gitignore in AudioSource
   - Result: Only track folder structure

4. **Process Management**
   - Problem: Hanging processes
   - Solution: Added cleanup.bat
   - Added proper process termination

### 4. FFmpeg Configuration
```bash
ffmpeg -hide_banner -loglevel info \
       -f concat -safe 0 -i playlist.m3u \
       -ac 2 -ar 44100 \
       -acodec pcm_s16le \
       -af aresample=async=1000 \
       -buffer_size 1024 \
       -f wav -
```

### 5. Directory Structure
```
virtual_dj_master/
├── AudioSource/           # Music library
│   └── .gitignore        # Ignore audio files
├── virtual_dj.py         # Main engine
├── now_playing.txt       # Current status
├── Playlist.m3u         # Active playlist
└── played_songs.log     # History
```

## Best Practices

1. **Audio File Organization**
   - Use consistent folder structure
   - Follow Artist/Album/Track naming
   - Keep files in AudioSource directory

2. **Process Management**
   - Always use cleanup.bat before closing
   - Let processes terminate gracefully
   - Monitor now_playing.txt for status

3. **Error Recovery**
   - System auto-restarts on crash
   - Maintains play history
   - Regenerates playlists as needed

## Known Limitations

1. No real-time volume control
2. Requires specific folder structure
3. Limited to MP3/WAV formats
4. Windows-specific paths

## Future Improvements

1. Add volume normalization
2. Implement crossfading
3. Add remote control interface
4. Support more audio formats