import os
import random
import json
import time
import subprocess
import sys
import psutil
from threading import Thread

# CONFIGURATION
AUDIO_SOURCE = "AudioSource"
PLAYLIST_FILE = "Playlist.m3u"
LOG_FILE = "played_songs.log"
VIRTUAL_CABLE_NAME = "CABLE Input (VB-Audio Virtual Cable)"
OBS_PATH = r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"
FFMPEG_PATH = r"C:\Program Files\FFMPEG\ffmpeg-2025-02-13-git-19a2d26177-full_build\bin\ffmpeg.exe"
VIRTUAL_CABLE_VARIANTS = [
    "CABLE Input (VB-Audio Virtual Cable)",
    "CABLE Input",
    "VB-Audio Virtual Cable",
    "Virtual Cable",
    "CABLE Output",
    "CABLE-A Input",
    "CABLE-B Input",
    "VB-Cable",
    "CABLE Output (VB-Audio Virtual Cable)"
]

class AudioDevices:
    """Class to handle audio device management"""
    def __init__(self):
        self.device_name = "CABLE Input (VB-Audio Virtual Cable)"
        
    def set_device(self, name):
        self.device_name = name
        
    def get_device(self):
        return self.device_name

# Create global instance
audio_devices = AudioDevices()

def check_dependencies():
    """Verify all required components are available"""
    print("\n=== Dependency Check ===")
    
    # First verify FFmpeg can run
    try:
        print("Checking FFmpeg devices...")
        dshow_check = subprocess.run(
            [
                FFMPEG_PATH,
                '-hide_banner',
                '-f', 'dshow',
                '-list_devices', 'true',
                '-i', 'dummy'
            ],
            capture_output=True,
            text=True
        )
        
        # The "Error opening input file dummy" is expected and normal
        # We just need to verify that devices were listed before that error
        if '"CABLE Output (VB-Audio Virtual Cable)" (audio)' in dshow_check.stderr:
            print("[OK] Found VB-Audio Virtual Cable")
            print("[OK] DirectShow support verified")
            
            # Extract the exact device name and ID
            for line in dshow_check.stderr.split('\n'):
                if 'CABLE Output (VB-Audio Virtual Cable)' in line:
                    if 'Alternative name' in line:
                        # Use the device ID for better compatibility
                        device_id = line.split('"')[1]
                        audio_devices.set_device(device_id)
                    else:
                        # Use the friendly name as fallback
                        audio_devices.set_device("CABLE Output (VB-Audio Virtual Cable)")
                    break
        else:
            print("[X] VB-Audio Virtual Cable not found")
            print("\nAvailable audio devices:")
            print(dshow_check.stderr)
            return False

        print(f"[OK] Using audio device: {audio_devices.get_device()}")
        return True

    except Exception as e:
        print(f"[X] FFmpeg test failed: {str(e)}")
        return False

def check_audio_device():
    """Enhanced audio device detection without global variables"""
    try:
        # Windows PowerShell device listing
        ps_cmd = 'Get-WmiObject Win32_SoundDevice | Select-Object Name, Status | Format-List'
        ps_process = subprocess.run(['powershell', '-Command', ps_cmd], 
                                  capture_output=True, 
                                  text=True)
        
        print("\nWindows Audio Devices:")
        print(ps_process.stdout)
        
        # FFmpeg device listing
        cmd1 = [FFMPEG_PATH, '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy']
        cmd2 = [FFMPEG_PATH, '-f', 'dshow', '-list_options', 'true', '-i', 'audio=dummy']
        
        for cmd in [cmd1, cmd2]:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.stderr:
                    print("\nFFmpeg device listing output:")
                    print(result.stderr)
                    
                    stderr_lower = result.stderr.lower()
                    for variant in VIRTUAL_CABLE_VARIANTS:
                        if variant.lower() in stderr_lower:
                            lines = result.stderr.split('\n')
                            for line in lines:
                                if variant.lower() in line.lower():
                                    if '"' in line:
                                        detected_name = line.split('"')[1]
                                    else:
                                        detected_name = line.strip().split(")")[-1].strip()
                                    
                                    if detected_name:
                                        print(f"\n[OK] Found Virtual Cable: {detected_name}")
                                        audio_devices.set_device(detected_name)
                                        return True
            except Exception as e:
                print(f"Method failed: {e}")
                continue
        
        print("\n[X] VB-Audio Cable not found!")
        print("\nTroubleshooting steps:")
        print("1. Open Windows Sound settings")
        print("2. Check if 'CABLE Input' appears in both Playback and Recording")
        print("3. If disabled, right-click and enable it")
        print("4. Try setting it as the default device")
        print("5. Restart your computer if recently installed")
        print("\nExpected device names:")
        for variant in VIRTUAL_CABLE_VARIANTS:
            print(f"- {variant}")
        return False
        
    except Exception as e:
        print(f"Error checking audio devices: {e}")
        return False

def start_stream(playlist_file):
    """Start audio stream with basic settings"""
    if not check_audio_device():
        return False, False

    # Use simple, working FFmpeg command
    command = [
        FFMPEG_PATH,
        '-hide_banner',
        '-loglevel', 'debug',
        '-stream_loop', '-1',
        '-f', 'concat',
        '-safe', '0',
        '-i', playlist_file,
        '-ac', '2',           # Force stereo
        '-ar', '44100',       # Standard sample rate
        '-acodec', 'pcm_s16le',
        '-af', 'aresample=async=1000',  # Handle async audio
        '-buffer_size', '1024',
        '-f', 'wav',
        '-'
    ]

    try:
        ffmpeg_process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        # Pipe to ffplay
        ffplay_cmd = [
            os.path.join(os.path.dirname(FFMPEG_PATH), 'ffplay'),
            '-f', 'wav',
            '-nodisp',
            '-autoexit',
            '-loglevel', 'quiet',
            '-'
        ]
        
        ffplay_process = subprocess.Popen(
            ffplay_cmd,
            stdin=ffmpeg_process.stdout,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        return ffmpeg_process, ffplay_process
        
    except Exception as e:
        print(f"Error starting stream: {e}")
        return False, False

def kill_existing_processes():
    """Kill any existing FFmpeg or OBS processes"""
    killed = False
    try:
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                # Check for FFmpeg and OBS processes
                if proc.info['name'].lower() in ['ffmpeg.exe', 'ffplay.exe', 'obs64.exe']:
                    process = psutil.Process(proc.info['pid'])
                    print(f"Killing existing {proc.info['name']} (PID: {proc.info['pid']})")
                    process.kill()
                    killed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        print(f"Error checking processes: {e}")
    
    if killed:
        print("Waiting for processes to close...")
        time.sleep(2)

def check_audio_files():
    """Check for audio files recursively in all configured locations"""
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    audio_sources = config['audio_sources']
    audio_files = []
    
    print("\nScanning for audio files...")
    for source in audio_sources:
        if not os.path.exists(source):
            print(f"\nWarning: Source folder not found: {source}")
            continue
            
        print(f"\nScanning: {source}")
        for root, _, files in os.walk(source):
            for file in files:
                if file.lower().endswith(('.mp3', '.wav', '.flac')):
                    audio_files.append(os.path.join(root, file))

    if not audio_files:
        print(f"\n[ERROR] No audio files found in any source folders:")
        for source in audio_sources:
            print(f"- {source}")
        print("\nPlease add supported audio files:")
        print("- MP3 files (*.mp3)")
        print("- WAV files (*.wav)")
        print("- FLAC files (*.flac)")
        return False

    print(f"\nFound {len(audio_files)} audio files total")
    return True

class CurrentSong:
    def __init__(self):
        self.title = "No song playing"
        self.artist = "Unknown"
        self.album = "Unknown"
        self.start_time = 0
        self.duration = 0
        self.path = ""

    def update(self, file_path):
        # Extract info from path structure: AudioSource/Artist/Album/XX - Title.mp3
        parts = os.path.normpath(file_path).split(os.sep)
        try:
            if len(parts) >= 4:  # Full artist/album structure
                self.artist = parts[-3]  # Artist folder name
                self.album = parts[-2]   # Album folder name
                title = os.path.splitext(parts[-1])[0]  # Remove extension
                self.title = title.split(" - ", 1)[1] if " - " in title else title
            else:
                self.title = os.path.splitext(os.path.basename(file_path))[0]
            
            self.path = file_path
            self.start_time = time.time()
            # Get audio duration using ffprobe
            result = subprocess.run([
                os.path.join(os.path.dirname(FFMPEG_PATH), 'ffprobe'),
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                file_path
            ], capture_output=True, text=True)
            self.duration = float(result.stdout)
            return True
        except Exception as e:
            print(f"Error parsing song info: {e}")
            return False

    def get_status(self):
        if not self.start_time:
            return "Waiting..."
        
        elapsed = time.time() - self.start_time
        remaining = max(0, self.duration - elapsed)
        timestamp = f"{int(remaining/60)}:{int(remaining%60):02d}"
        
        return f"{self.artist} - {self.title} ({timestamp})"

class VirtualDJ:
    def __init__(self):
        self.ffmpeg_process = None
        self.obs_process = None
        self.running = True
        self.playlist_update_interval = 10800  # 3 hours in seconds
        self.current_song = CurrentSong()
        self.last_status_update = 0
        self.status_update_interval = 1  # Update every second
        self.songs_in_playlist = 0
        self.songs_played = 0

        # Load configuration
        with open('config.json', 'r') as f:
            self.config = json.load(f)

    def _generate_playlist(self):
        """Create shuffled playlist with recursive folder support"""
        try:
            # Recursive search for audio files
            all_songs = []
            for source in self.config['audio_sources']:
                for root, _, files in os.walk(source):
                    for file in files:
                        if file.lower().endswith(('.mp3', '.wav', '.flac')):
                            full_path = os.path.abspath(os.path.join(root, file))
                            all_songs.append(full_path)

            if not all_songs:
                raise Exception("No audio files found in source directories")

            print(f"\nFound {len(all_songs)} total audio files")

            # Create shuffled playlist
            random.shuffle(all_songs)
            self.songs_in_playlist = len(all_songs)
            self.songs_played = 0

            # Write playlist
            with open(PLAYLIST_FILE, "w", encoding='utf-8') as f:
                for song in all_songs:
                    escaped_path = song.replace("'", "'\\''")
                    f.write(f"file '{escaped_path}'\n")

            print(f"Created new playlist with {self.songs_in_playlist} songs")
            return True

        except Exception as e:
            print(f"Error generating playlist: {str(e)}")
            return False

    def _verify_playlist(self, playlist_file):
        """Verify playlist integrity"""
        try:
            # Check if FFmpeg can read the playlist
            cmd = [
                FFMPEG_PATH,
                '-v', 'error',
                '-f', 'concat',
                '-safe', '0',
                '-i', playlist_file,
                '-f', 'null',
                '-'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

    def _start_ffmpeg(self):
        """Start FFmpeg with better process handling"""
        print("\n=== Starting FFmpeg ===")
        
        # Kill any existing FFmpeg process
        if self.ffmpeg_process:
            try:
                self.ffmpeg_process.terminate()
                time.sleep(2)
                if self.ffmpeg_process.poll() is None:
                    self.ffmpeg_process.kill()
            except:
                pass

        # Start new FFmpeg process
        process = start_stream(PLAYLIST_FILE)
        if not process:
            print("[X] FFmpeg failed to start - check error messages above")
            return False
            
        self.ffmpeg_process = process
        print("[OK] FFmpeg started successfully")
        return True

    def _start_obs(self):
        """Launch OBS with better process handling"""
        print("\n=== Starting OBS ===")
        obs_bin_dir = os.path.dirname(OBS_PATH)
        print(f"OBS directory: {obs_bin_dir}")
        
        if self.obs_process and self.obs_process.poll() is None:
            print("Terminating existing OBS process...")
            self.obs_process.terminate()
            time.sleep(2)
            
        try:
            self.obs_process = subprocess.Popen(
                [OBS_PATH, "--startstreaming"],
                cwd=obs_bin_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Give OBS time to start and check if it's running
            for _ in range(5):  # Try for 10 seconds
                time.sleep(2)
                if self.obs_process.poll() is None:
                    # Check if OBS is actually running
                    for proc in psutil.process_iter(['name']):
                        if 'obs64.exe' in proc.info['name'].lower():
                            print("[OK] OBS started successfully")
                            return True
            
            # If we get here, OBS failed to start properly
            stdout, stderr = self.obs_process.communicate()
            print("[X] OBS failed to start")
            print("Error details:")
            if stdout: print(f"Output: {stdout.decode()}")
            if stderr: print(f"Error: {stderr.decode()}")
            
            print("\nTroubleshooting steps:")
            print("1. Try starting OBS manually first")
            print("2. Check if OBS is already running")
            print("3. Verify OBS installation at:", OBS_PATH)
            print("4. Run this script as administrator")
            return False
            
        except Exception as e:
            print(f"[X] Error starting OBS: {e}")
            return False

    def _playlist_updater(self):
        """Removed automatic playlist updates since we now update after all songs are played"""
        while self.running:
            time.sleep(60)  # Just keep thread alive with minimal overhead

    def _watchdog(self):
        """Monitor and restart failed processes with improved retry logic"""
        consecutive_failures = 0
        while self.running:
            if self.ffmpeg_process and self.ffmpeg_process.poll() is not None:
                print(f"FFmpeg crashed! Attempt {consecutive_failures + 1}")
                
                # Get error output
                stderr = self.ffmpeg_process.stderr.read().decode()
                if stderr:
                    print(f"FFmpeg error: {stderr}")
                
                # Retry with increasing delay
                time.sleep(min(consecutive_failures * 2, 30))  # Max 30 second delay
                if self._start_ffmpeg():
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    
                # If too many failures, regenerate playlist
                if consecutive_failures >= 3:
                    print("Multiple FFmpeg failures, regenerating playlist...")
                    self._generate_playlist()
                    consecutive_failures = 0
                    
            if self.obs_process and self.obs_process.poll() is not None:
                print("OBS crashed! Restarting...")
                self._start_obs()
                
            time.sleep(5)

    def _update_status_file(self):
        """Write current status to file"""
        try:
            with open("now_playing.txt", "w", encoding='utf-8') as f:
                f.write(f"{self.current_song.title}\n")
                f.write(f"{self.current_song.artist} // {self.current_song.album}\n")
        except Exception as e:
            print(f"Error writing status: {e}")

    def monitor_ffmpeg_output(self, process):
        """Monitor FFmpeg output for song changes"""
        try:
            while process.poll() is None and self.running:
                line = process.stderr.readline().decode().strip()
                if not line:
                    continue
                    
                # Detect song changes
                if "Opening '" in line:
                    file_path = line.split("'")[1]
                    if file_path.endswith(('.mp3', '.wav', '.flac')):
                        self.songs_played += 1
                        if self.current_song.update(file_path):
                            print(f"\nNow Playing: {self.current_song.get_status()}")
                            print(f"Progress: {self.songs_played}/{self.songs_in_playlist} songs played")
                            self._update_status_file()
                            
                            # Check if all songs have been played
                            if self.songs_played >= self.songs_in_playlist:
                                print("\n=== All songs have been played! Generating new playlist... ===")
                                self._generate_playlist()
                                self._start_ffmpeg()
                
                # Regular status updates
                current_time = time.time()
                if current_time - self.last_status_update >= self.status_update_interval:
                    if "size=" in line:  # Progress indicator
                        print(f"\r{self.current_song.get_status()} ({self.songs_played}/{self.songs_in_playlist})", end='', flush=True)
                        self._update_status_file()
                        self.last_status_update = current_time
                    
        except Exception as e:
            print(f"Monitor error: {e}")
            self._update_status_file()

    def run(self):
        """Ensure clean startup"""
        if not check_dependencies():
            sys.exit(1)
            
        print("\n=== Checking for existing processes ===")
        kill_existing_processes()
            
        if not check_audio_files():
            sys.exit(1)

        print("\n=== Starting Virtual DJ ===")
        print("1. Starting OBS...")
        
        # Try starting OBS up to 3 times
        for attempt in range(3):
            if attempt > 0:
                print(f"\nRetrying OBS startup (attempt {attempt + 1}/3)...")
                time.sleep(5)
                
            if self._start_obs():
                print("2. Waiting for OBS to initialize...")
                time.sleep(15)
                break
        else:
            print("[X] Failed to start OBS after 3 attempts")
            sys.exit(1)
        
        print("3. Generating playlist...")
        if not self._generate_playlist():
            print("Failed to generate playlist")
            sys.exit(1)
        
        print("4. Starting FFmpeg stream...")
        ffmpeg_process, ffplay_process = start_stream(PLAYLIST_FILE)
        if not ffmpeg_process or not ffplay_process:
            print("Failed to start FFmpeg")
            sys.exit(1)
        
        self.ffmpeg_process = ffplay_process  # Store ffplay process for watchdog
        print("\n[OK] All systems running!")
        
        # Start monitoring threads
        Thread(target=self._playlist_updater, daemon=True).start()
        Thread(target=self._watchdog, daemon=True).start()
        Thread(target=lambda: self.monitor_ffmpeg_output(ffmpeg_process), daemon=True).start()

        # Write initial status
        self._update_status_file()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.running = False
            if ffmpeg_process:
                ffmpeg_process.terminate()
            if ffplay_process:
                ffplay_process.terminate()
            print("Stream stopped.")

if __name__ == "__main__":
    if not os.path.exists("Playlist.m3u"):
        print("Error: Playlist.m3u not found")
        sys.exit(1)

    dj = VirtualDJ()
    dj.run()