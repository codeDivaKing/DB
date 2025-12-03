class EventDeduper:
    def __init__(self, window_seconds: int):
        self.window = window_seconds
        self.last_seen = {}   # event_name -> last timestamp


    def should_print(self, event_name: str, timestamp: int) -> bool:
        """
        Return True if the event should be printed,
        and update internal state accordingly.
        """
        if event_name in self.last_seen:
            if self.last_seen[event_name] + self.window > timestamp:
                return False
            else:
                del self.last_seen[event_name]
        self.last_seen[event_name] = timestamp
        return True

    def cleanup(self, now: int):
        """Remove expired entries (lazy / cronjob)."""
        for name, time in self.last_seen.items():
            if time + self.window < now:
                del self.last_seen[name]
        return
