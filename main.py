from playback_watchdog import PlaybackWatchdog

class PlaybackManager:
    def __init__(self):
        self.watchdog = PlaybackWatchdog(timeout_seconds=10)
        # ...existing code...

    def process_cmd(self):
        self.watchdog.update_cmd_timestamp()
        # ...existing code...

    def update_now_playing(self):
        self.watchdog.update_now_playing_timestamp()
        # ...existing code...

    def play(self):
        self.watchdog.set_playing_status(True)
        # ...existing code...

    def stop(self):
        self.watchdog.set_playing_status(False)
        # ...existing code...

    def main_loop(self):
        while True:
            # ...existing code...
            if not self.watchdog.check_status():
                self.logger.error("Watchdog triggered - forcing playback reset")
                self.stop()
                self.reset_playback()
                self.watchdog.reset_timestamps()
            time.sleep(0.1)
