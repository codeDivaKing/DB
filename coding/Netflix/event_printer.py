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


class EventDeduper:
    def __init__(self, window_seconds: int):
        self.window = window_seconds
        self.events = {}  # name -> SortedDict of timestamps

    def should_print(self, name: str, ts: int) -> bool:
        if name not in self.events:
            self.events[name] = SortedDict()

        sd = self.events[name]
        low = ts - self.window

        # ---------------------------
        # 1. Prune expired timestamps
        # ---------------------------
        stale = []
        for t in sd.keys:      # sd.keys is sorted small→large
            if t < low:
                stale.append(t)
            else:
                break
        for t in stale:
            del sd[t]

        # ---------------------------
        # 2. Check if any timestamp in window [low, ts]
        # ---------------------------
        # After pruning, if first key exists and <= ts → duplicate
        if sd.keys:
            if sd.keys[0] <= ts:   # earliest still-valid timestamp
                return False

        # ---------------------------
        # 3. Insert new timestamp
        # ---------------------------
        sd[ts] = True
        return True
