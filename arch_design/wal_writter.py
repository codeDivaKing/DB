import threading, queue, os

class WALWriter:
    def __init__(self, file_path):
        self.log_file = open(file_path, "ab", buffering=0)
        self.queue = queue.Queue()
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._writer_loop, daemon=True)
        self.thread.start()

    def submit(self, data: bytes):
        event = threading.Event()
        self.queue.put((data, event))
        event.wait()   # wait until fsync done
        return True

    def _writer_loop(self):
        while True:
            # batch collect
            batch = []
            try:
                data, event = self.queue.get(timeout=0.01)
                batch.append((data, event))
            except queue.Empty:
                continue

            # drain rest of queue for batching
            while not self.queue.empty():
                batch.append(self.queue.get_nowait())

            # sequential write
            with self.lock:
                for data, _ in batch:
                    self.log_file.write(data)
                self.log_file.flush()
                os.fsync(self.log_file.fileno())

            # notify all threads in batch
            for _, event in batch:
                event.set()
