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


import time

class KVCache:
    def __init__(self, default_ttl=None):
        self.store = {}             # key -> entry dict
        self.default_ttl = default_ttl

    def _now(self):
        return int(time.time())

    # ------------------------
    # PUT
    # ------------------------
    def put(self, key, value, ttl=None):
        expire_at = None
        if ttl is not None:
            expire_at = self._now() + ttl
        elif self.default_ttl is not None:
            expire_at = self._now() + self.default_ttl

        self.store[key] = {
            "value": value,
            "deleted": False,
            "expire_at": expire_at
        }

    # ------------------------
    # GET
    # ------------------------
    def get(self, key):
        entry = self.store.get(key)
        if not entry:
            return None

        # Lazy check for expiration
        if entry["expire_at"] and entry["expire_at"] <= self._now():
            entry["deleted"] = True
            return None

        # Lazy delete check
        if entry["deleted"]:
            return None

        return entry["value"]

    # ------------------------
    # LAZY DELETE
    # ------------------------
    def delete(self, key):
        if key in self.store:
            self.store[key]["deleted"] = True

    # ------------------------
    # CRON JOB CLEANUP
    # ------------------------
    def cron_job_cleanup(self):
        now = self._now()

        keys_to_delete = []
        for key, entry in self.store.items():
            expired = entry["expire_at"] and entry["expire_at"] <= now
            if entry["deleted"] or expired:
                keys_to_delete.append(key)

        # Remove them fully
        for key in keys_to_delete:
            del self.store[key]
