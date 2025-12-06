import time
from collections import deque

class RateLimiter:
    def __init__(self, ttl, limit):
        # TODO: Implement __init__ logic.
        
        self.limit = limit
        self.ttl = ttl
        self.queue = deque()

    def allowRequest(self):
        # TODO: Implement allowRequest logic.
        now = int(time.time() * 1000)
        while self.queue and self.queue[0] + self.ttl <= now:
            self.queue.popleft()
        if len(self.queue) >= self.limit:
            return False
        else:
            self.queue.append(now)
            return True

def main():
    test1()
    test2()

def test1():
    print("========= Test 1 =========")
    rateLimiter = RateLimiter(1000, 5)

    # Make 11 requests at a rate faster than the rate limiter allows
    for i in range(11):
        print(f"Request {i + 1} accepted (t={i * 100}ms)? : {rateLimiter.allowRequest()}")
        time.sleep(0.1)  # Sleep for 100 milliseconds between requests

def test2():
    print("\n========= Test 2 =========")
    rateLimiter = RateLimiter(1000, 5)

    # Make 10 requests at a rate slower than the rate limiter allows
    for i in range(10):
        print(f"Request {i + 1} accepted (t={i * 300}ms)? : {rateLimiter.allowRequest()}")
        time.sleep(0.3)  # Sleep for 300 milliseconds between requests

if __name__ == "__main__":
    main()