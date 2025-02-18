import logging
import time
from datetime import datetime

class PlaybackWatchdog:
    def __init__(self, timeout_seconds=10):
        self.timeout_seconds = timeout_seconds
        self.last_cmd_update = None
        self.last_now_playing_update = None
        self.is_playing = False
        self.logger = logging.getLogger('PlaybackWatchdog')

    def update_cmd_timestamp(self):
        self.last_cmd_update = datetime.now()

    def update_now_playing_timestamp(self):
        self.last_now_playing_update = datetime.now()

    def set_playing_status(self, is_playing):
        self.is_playing = is_playing

    def check_status(self):
        if not self.is_playing:
            return True

        now = datetime.now()
        
        if self.last_cmd_update and self.last_now_playing_update:
            cmd_diff = (now - self.last_cmd_update).total_seconds()
            now_playing_diff = (now - self.last_now_playing_update).total_seconds()

            if cmd_diff > self.timeout_seconds or now_playing_diff > self.timeout_seconds:
                self.logger.warning(f"Watchdog timeout detected! CMD: {cmd_diff:.1f}s, Now Playing: {now_playing_diff:.1f}s")
                return False

        return True

    def reset_timestamps(self):
        self.last_cmd_update = None
        self.last_now_playing_update = None
        self.is_playing = False
