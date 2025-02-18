import logging
import time
from datetime import datetime, timedelta

class PlaybackWatchdog:
    def __init__(self, timeout_seconds=10, max_skips=3):
        self.timeout_seconds = timeout_seconds
        self.last_cmd_update = datetime.now()  # Initialize with current time
        self.last_now_playing_update = datetime.now()  # Initialize with current time
        self.is_playing = False
        self.is_initialized = False
        self.logger = logging.getLogger('PlaybackWatchdog')
        self.current_song = None
        self.song_start_time = None
        self.skip_count = 0
        self.max_skips = max_skips
        self.expected_end_time = None
        
    def initialize(self):
        self.is_initialized = True
        self.reset_timestamps()
        self.logger.info("Watchdog initialized")

    def update_cmd_timestamp(self):
        if not self.is_initialized:
            self.initialize()
        self.last_cmd_update = datetime.now()
        self.logger.debug(f"CMD timestamp updated: {self.last_cmd_update}")

    def update_now_playing_timestamp(self):
        if not self.is_initialized:
            self.initialize()
        self.last_now_playing_update = datetime.now()
        self.logger.debug(f"Now Playing timestamp updated: {self.last_now_playing_update}")

    def set_playing_status(self, is_playing):
        self.is_playing = is_playing

    def update_song(self, song_info, duration_seconds):
        if self.current_song != song_info:
            if self.current_song is not None:
                self._check_premature_skip()
            
            self.current_song = song_info
            self.song_start_time = datetime.now()
            self.expected_end_time = self.song_start_time + \
                timedelta(seconds=duration_seconds)
            self.logger.info(f"New song: {song_info}, Duration: {duration_seconds}s")

    def _check_premature_skip(self):
        if self.expected_end_time and datetime.now() < self.expected_end_time:
            time_remaining = (self.expected_end_time - datetime.now()).total_seconds()
            if time_remaining > 5:  # Only count as skip if more than 5 seconds remaining
                self.skip_count += 1
                self.logger.warning(f"Premature skip detected! {time_remaining:.1f}s remaining. Skip count: {self.skip_count}")
        else:
            self.skip_count = 0

    def check_status(self):
        if not self.is_playing:
            return True

        now = datetime.now()
        
        # Check for too many consecutive skips
        if self.skip_count >= self.max_skips:
            self.logger.error(f"Too many consecutive skips ({self.skip_count})!")
            return False

        # Check for timeouts
        if self.last_cmd_update and self.last_now_playing_update:
            cmd_diff = (now - self.last_cmd_update).total_seconds()
            now_playing_diff = (now - self.last_now_playing_update).total_seconds()

            if cmd_diff > self.timeout_seconds or now_playing_diff > self.timeout_seconds:
                self.logger.warning(f"Watchdog timeout! CMD: {cmd_diff:.1f}s, Now Playing: {now_playing_diff:.1f}s")
                return False

        return True

    def reset_timestamps(self):
        self.last_cmd_update = None
        self.last_now_playing_update = None
        self.is_playing = False
        self.current_song = None
        self.song_start_time = None
        self.skip_count = 0
        self.expected_end_time = None
