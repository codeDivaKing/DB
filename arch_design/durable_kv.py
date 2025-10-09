# https://chatgpt.com/s/t_68e81e45985c8191b8969fcae527d628
# durable_kv.py
import os
import json
import threading
import time
import tempfile

# ---------- Simple readers-writer lock ----------
class RWLock:
    """
    Simple readers-writer lock:
    - acquire_read(): multiple readers allowed concurrently.
    - acquire_write(): exclusive.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._read_ready = threading.Condition(self._lock)
        self._readers = 0
        self._writer = False

    def acquire_read(self):
        with self._lock:
            while self._writer:
                self._read_ready.wait()
            self._readers += 1

    def release_read(self):
        with self._lock:
            self._readers -= 1
            if self._readers == 0:
                self._read_ready.notify_all()

    def acquire_write(self):
        with self._lock:
            while self._writer or self._readers > 0:
                self._read_ready.wait()
            self._writer = True

    def release_write(self):
        with self._lock:
            self._writer = False
            self._read_ready.notify_all()


# ---------- WAL Manager ----------
class WALManager:
    """
    Manage append-only WAL file rotation.
    WAL files named: wal_{seq}.log (seq is integer).
    Each WAL line: JSON { "seq": <wal_seq>, "entry_id": <monotonic entry id>, "op": "PUT"/"DEL", "key": <k>, "value": <v or null> }
    """
    def __init__(self, dirpath):
        os.makedirs(dirpath, exist_ok=True)
        self.dirpath = dirpath
        self._meta_lock = threading.Lock()    # protects rotation and current wal handle
        self._append_lock = threading.Lock()  # serialize appends so they are ordered in file
        self.current_seq = self._discover_latest_seq()
        self.wal_file = open(self._wal_path(self.current_seq), "a+b")
        self.entry_counter = 0

    def _wal_path(self, seq):
        return os.path.join(self.dirpath, f"wal_{seq}.log")

    def _discover_latest_seq(self):
        # find largest wal_N.log; if none, start at 1
        files = os.listdir(self.dirpath)
        seqs = [int(fname.split("_")[1].split(".")[0]) 
                for fname in files if fname.startswith("wal_") and fname.endswith(".log")]
        return max(seqs) + 1 if seqs else 1

    def append(self, op, key, value):
        """
        Append a WAL entry and ensure it's flushed to disk (fsync).
        Returns a (wal_seq, entry_id) tuple.
        """
        with self._append_lock:
            self.entry_counter += 1
            entry = {
                "wal_seq": self.current_seq,
                "entry_id": self.entry_counter,
                "op": op,
                "key": key,
                "value": value
            }
            line = (json.dumps(entry) + "\n").encode("utf-8")
            with self._meta_lock:
                self.wal_file.write(line)
                self.wal_file.flush()
                os.fsync(self.wal_file.fileno())
            return (self.current_seq, self.entry_counter)

    def rotate(self, new_seq=None):
        """
        Rotate WAL: close current file and open a new one with higher sequence.
        Caller must ensure snapshot coordination.
        """
        with self._meta_lock:
            self.wal_file.flush()
            os.fsync(self.wal_file.fileno())
            self.wal_file.close()
            if new_seq is None:
                new_seq = self.current_seq + 1
            self.current_seq = new_seq
            self.wal_file = open(self._wal_path(self.current_seq), "a+b")
            # reset entry counter for readability (optional)
            self.entry_counter = 0
            return self.current_seq

    def list_wal_seqs(self):
        files = os.listdir(self.dirpath)
        seqs = sorted(int(fname.split("_")[1].split(".")[0]) 
                      for fname in files if fname.startswith("wal_") and fname.endswith(".log"))
        return seqs

    def close(self):
        with self._meta_lock:
            try:
                self.wal_file.flush()
                os.fsync(self.wal_file.fileno())
                self.wal_file.close()
            except:
                pass

# ---------- KV Store ----------
class DurableKV:
    def __init__(self, data_dir, n_shards=16):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.n_shards = n_shards
        self.shards = [dict() for _ in range(n_shards)]
        self.shard_locks = [RWLock() for _ in range(n_shards)]
        self.wal = WALManager(data_dir)
        self._key_lock = threading.Lock()  # protects helper operations if needed

    def _shard_index(self, key):
        return hash(key) % self.n_shards

    # ---------- public API ----------
    def get(self, key):
        idx = self._shard_index(key)
        lock = self.shard_locks[idx]
        lock.acquire_read()
        try:
            return self.shards[idx].get(key, None)
        finally:
            lock.release_read()

    def put(self, key, value):
        """
        Write path:
        1. Append to WAL and fsync (to ensure durability).
        2. Acquire shard write lock and apply to memory.
        """
        # 1) append WAL (serialize append across writers)
        wal_seq, entry_id = self.wal.append("PUT", key, value)
        # 2) apply in-memory under shard lock (short critical section)
        idx = self._shard_index(key)
        lock = self.shard_locks[idx]
        lock.acquire_write()
        try:
            self.shards[idx][key] = value
        finally:
            lock.release_write()
        return (wal_seq, entry_id)

    def delete(self, key):
        wal_seq, entry_id = self.wal.append("DEL", key, None)
        idx = self._shard_index(key)
        lock = self.shard_locks[idx]
        lock.acquire_write()
        try:
            self.shards[idx].pop(key, None)
        finally:
            lock.release_write()
        return (wal_seq, entry_id)

    # ---------- snapshot ----------
    def snapshot(self):
        """
        Create a consistent snapshot:
        - Acquire all shard write locks in a fixed order (to block writers briefly).
        - Dump in-memory map to a temp file.
        - fsync and atomically rename to snapshot_{seq}.snap (seq = current wal seq)
        - Rotate the WAL after snapshot to start a new WAL file.
        """
        # Acquire all shard write locks IN ORDER to get a consistent view
        for lock in self.shard_locks:
            lock.acquire_write()
        try:
            # Choose snapshot seq to be wal.current_seq (so this snapshot includes all entries
            # up to wal.current_seq - 1 that have been applied)
            snapshot_seq = self.wal.current_seq
            tmp_fd, tmp_path = tempfile.mkstemp(dir=self.data_dir, prefix="snaptmp_")
            os.close(tmp_fd)
            snap_info = {
                "snapshot_seq": snapshot_seq,
                "created_at": time.time()
            }
            # Dump entire store as JSON (for demo; for large systems prefer binary/formatted snapshots)
            aggregate = {}
            for shard in self.shards:
                aggregate.update(shard)
            with open(tmp_path, "w") as f:
                # write metadata + data
                f.write(json.dumps({"meta": snap_info, "data": aggregate}))
                f.flush()
                os.fsync(f.fileno())
            # atomically move into place
            final_name = os.path.join(self.data_dir, f"snapshot_{snapshot_seq}.snap")
            os.replace(tmp_path, final_name)
            # Now that snapshot is durable, rotate WAL so new writes go into wal_{snapshot_seq+1}.log
            new_wal_seq = snapshot_seq + 1
            self.wal.rotate(new_seq=new_wal_seq)
            return final_name
        finally:
            for lock in reversed(self.shard_locks):
                lock.release_write()

    # ---------- recovery ----------
    def recover(self):
        """
        1. Find latest snapshot (largest snapshot_N).
        2. Load it into memory.
        3. Apply WAL files with seq >= snapshot_seq (or > snapshot_seq depending on protocol).
           Using our protocol, snapshot_seq was chosen as wal.current_seq at snapshot time and
           we rotated WAL to snapshot_seq+1 immediately. Therefore WALs with seq == snapshot_seq
           contain entries BEFORE snapshot or partial; to be safe we will:
             - choose snapshot_seq from snapshot meta and then apply WAL files with seq >= snapshot_seq
               (but careful to avoid applying entries duplicated in snapshot).
           Simpler: snapshot contains full state up to snapshot_seq-1 and we rotate to snapshot_seq+1.
           For safety in this code we'll:
             - load snapshot.meta.snapshot_seq -> s
             - apply all wal files with seq >= s and >= 1, in ascending order.
        """
        # clear current memory
        for idx in range(self.n_shards):
            self.shards[idx].clear()

        # find latest snapshot
        files = os.listdir(self.data_dir)
        snaps = [fname for fname in files if fname.startswith("snapshot_") and fname.endswith(".snap")]
        if snaps:
            # choose largest seq
            def snap_seq(name): return int(name.split("_")[1].split(".")[0])
            latest_snap = max(snaps, key=snap_seq)
            snap_path = os.path.join(self.data_dir, latest_snap)
            with open(snap_path, "r") as f:
                payload = json.load(f)
            meta = payload["meta"]
            snapshot_seq = meta["snapshot_seq"]
            data = payload["data"]
            # load into shards
            for k, v in data.items():
                idx = self._shard_index(k)
                self.shards[idx][k] = v
        else:
            snapshot_seq = 1  # no snapshot, start from 1

        # apply WALs with seq >= snapshot_seq
        wal_seqs = self.wal.list_wal_seqs()
        wal_seqs = [s for s in wal_seqs if s >= snapshot_seq]
        wal_seqs.sort()
        for s in wal_seqs:
            p = os.path.join(self.data_dir, f"wal_{s}.log")
            try:
                with open(p, "r") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        entry = json.loads(line)
                        op = entry["op"]
                        k = entry["key"]
                        if op == "PUT":
                            idx = self._shard_index(k)
                            self.shards[idx][k] = entry["value"]
                        elif op == "DEL":
                            idx = self._shard_index(k)
                            self.shards[idx].pop(k, None)
            except FileNotFoundError:
                continue
        return snapshot_seq

    def close(self):
        self.wal.close()


# ---------- Basic demo ----------
if __name__ == "__main__":
    import random
    import shutil
    DATADIR = "./kvdata_demo"
    if os.path.exists(DATADIR):
        shutil.rmtree(DATADIR)
    kv = DurableKV(DATADIR, n_shards=8)

    # write some keys
    for i in range(50):
        kv.put(f"key{i}", f"value-{i}")

    # snapshot
    snapfile = kv.snapshot()
    print("Snapshot created:", snapfile)

    # more writes
    for i in range(50, 70):
        kv.put(f"key{i}", f"value-{i}")

    # simulate restart: create new instance pointing to same dir
    kv2 = DurableKV(DATADIR, n_shards=8)
    kv2.recover()
    print("Recovered sample:", kv2.get("key60"), kv2.get("key10"))
    kv2.close()
    kv.close()
