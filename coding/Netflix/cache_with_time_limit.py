import time

class TimeLimitedCache:
    def __init__(self):
        self.cache = {}   # key -> { "value": ..., "expiration": ... }

    def set(self, key, value, duration):
        now = time.time() * 1000  # convert to ms like JS Date.now()
        has_unexpired = (
            key in self.cache and now < self.cache[key]["expiration"]
        )

        # store new entry
        self.cache[key] = {
            "value": value,
            "expiration": now + duration
        }

        return has_unexpired

    def get(self, key):
        now = time.time() * 1000
        entry = self.cache.get(key)

        if entry is None:
            return -1
        if now > entry["expiration"]:
            return -1
        return entry["value"]

    def count(self):
        now = time.time() * 1000
        c = 0
        for entry in self.cache.values():
            if now < entry["expiration"]:
                c += 1
        return c
