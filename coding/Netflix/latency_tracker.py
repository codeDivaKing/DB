from collections import defaultdict

class LatencyTracker:
    def __init__(self):
        self.latencies = defaultdict(list)

    def report(self, user_id, latency_ms):
        self.latencies[user_id].append(latency_ms)

    def query(self, user_id, percentile):
        latency = self.latencies[user_id]
        latency.sort()
        
        idx = int(percentile * len(latency)/100) - 1
        idx = max(idx, 0)
        return latency[idx]


tracker = LatencyTracker()
tracker.report("user1", 100)
tracker.report("user1", 200)
tracker.report("user1", 300)
tracker.report("user1", 400)
tracker.report("user1", 500)
tracker.report("user1", 600)
tracker.report("user1", 700)
tracker.report("user1", 800)
tracker.report("user1", 900)
tracker.report("user1", 1000)

print(tracker.query("user1", 50))
print(tracker.query("user1", 90))

class Latency:
    def __init__(self, bucket_size=5, max_latency=1000):
        self.bucket_size = bucket_size
        self.total = 0
        self.bucket_count = max_latency // bucket_size + 1
        self.buckets = [0] * self.bucket_count

    def report(self, latency_ms):
        idx = min(latency_ms // self.bucket_size, self.bucket_count - 1)
        self.buckets[idx] += 1
        self.total += 1
    
    def query(self, percentile):
        if self.total == 0:
            return None
        target = percentile * self.total / 100
        
        count = 0
        for i, cnt in enumerate(self.buckets):
            count += cnt
            if count >= target:
                return self.bucket_size * i
        return None


latency = Latency()
latency.report(100)
latency.report(200)
latency.report(300)
latency.report(400)
latency.report(500)
latency.report(600)
latency.report(700)
latency.report(800)
latency.report(900)
latency.report(1000)

print(latency.query(50))
print(latency.query(90))
