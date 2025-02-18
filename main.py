import logging
import signal
import psutil
import time
import os
import subprocess
import json
import sys
from pathlib import Path
from playback_watchdog import PlaybackWatchdog

try:
    import requests
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "requests"])
    import requests

class PlaybackManager:
    def __init__(self):
        # Initialize logging
        self.logger = logging.getLogger('PlaybackManager')
        
        # Load config and paths
        self.load_config()
        self.find_obs_path()
        
        # Initialize components
        self.watchdog = PlaybackWatchdog(timeout_seconds=10, max_skips=3)
        self.watchdog.initialize()
        
        # Setup OBS parameters
        self.obs_process = None
        self.ws = None  # WebSocket connection
        
        # Register shutdown handlers
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

    def load_config(self):
        """Load configuration file"""
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
            self.scene_name = self.config.get('scene_name', 'Scene')
            self.profile_name = self.config.get('profile_name', 'Default')
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            raise

    def find_obs_path(self):
        """Locate OBS installation"""
        paths = [
            r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
            r"C:\Program Files (x86)\obs-studio\bin\64bit\obs64.exe",
            os.path.expandvars(r"%PROGRAMFILES%\obs-studio\bin\64bit\obs64.exe"),
            os.path.expandvars(r"%PROGRAMFILES(X86)%\obs-studio\bin\64bit\obs64.exe")
        ]
        
        for path in paths:
            if os.path.exists(path):
                self.obs_path = path
                self.obs_dir = os.path.dirname(path)
                return
                
        raise FileNotFoundError("OBS installation not found")

    def start_obs(self):
        """Start OBS with safe mode disabled"""
        try:
            if self._is_obs_running():
                self.shutdown()
                time.sleep(2)

            # Create directory flag to disable shutdown check
            flag_file = Path(self.obs_dir) / 'disable-shutdown-check'
            flag_file.touch()

            # Launch OBS with minimal parameters
            cmd = [
                self.obs_path,
                '--minimize-to-tray',
                '--disable-shutdown-check',
                '--scene', self.scene_name,
                '--profile', self.profile_name,
                '--startstreaming'
            ]
            
            self.obs_process = subprocess.Popen(
                cmd, 
                cwd=self.obs_dir,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            time.sleep(5)  # Wait for OBS to start
            return self.obs_process is not None
            
        except Exception as e:
            self.logger.error(f"Error starting OBS: {e}")
            return False

    def shutdown(self):
        """Safely shutdown OBS"""
        try:
            if self.ws:
                try:
                    self.ws.call(requests.StopStreaming())
                    time.sleep(2)
                except:
                    pass
                self.ws.disconnect()

            if self._is_obs_running():
                os.system("taskkill /f /im obs64.exe")
                time.sleep(2)

            self.watchdog.reset_timestamps()
            self.logger.info("Shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info("Shutdown signal received")
        self.shutdown()
        sys.exit(0)

    def _is_obs_running(self):
        """Check if OBS is running"""
        return any('obs64.exe' in p.name().lower() for p in psutil.process_iter(['name'], exclude_access_denied=True))

    def process_cmd(self):
        try:
            self.watchdog.update_cmd_timestamp()
            # ...existing code...
        except Exception as e:
            self.logger.error(f"Error in process_cmd: {e}")

    def update_now_playing(self, song_info, duration_str):
        try:
            duration_seconds = self._parse_duration(duration_str)
            self.watchdog.update_song(song_info, duration_seconds)
            self.watchdog.update_now_playing_timestamp()
            # ...existing code...
        except Exception as e:
            self.logger.error(f"Error in update_now_playing: {e}")

    def _parse_duration(self, duration_str):
        """Convert duration string (MM:SS) to seconds"""
        try:
            minutes, seconds = map(int, duration_str.strip('()').split(':'))
            return minutes * 60 + seconds
        except:
            return 0

    def play(self):
        self.watchdog.set_playing_status(True)
        # ...existing code...

    def stop(self):
        self.watchdog.set_playing_status(False)
        # ...existing code...

    def reset_playback(self):
        self.shutdown()  # Safely shutdown OBS
        self.watchdog.reset_timestamps()
        # ...existing code...
        # Restart OBS with our parameters
        self.start_obs()
        # ...existing code...

    def main_loop(self):
        while True:
            try:
                # ...existing code...
                watchdog_status = self.watchdog.check_status()
                if not watchdog_status:
                    self.logger.warning("Watchdog detected playback issue")
                    self.stop()
                    self.reset_playback()
                    self.watchdog.reset_timestamps()
                # Check status more frequently
                time.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(1)  # Prevent rapid error loops
