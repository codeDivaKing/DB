import time
import threading
from collections import deque, defaultdict

class RateLimiter:
    def __init__(self, ttl, limit):
        # TODO: Implement __init__ logic.
        self.ttl = ttl
        self.limit = limit
        self.rate_limit_store = defaultdict(deque)


    def allowRequest(self, customerId):
        # TODO: Implement allowRequest logic.
        now = int(time.time() * 1000)
        queue = self.rate_limit_store[customerId]
        while queue and queue[0] + self.ttl <= now:
            queue.popleft()
        
        if len(queue) >= self.limit:
            return False
        else:
            queue.append(now)
            return True


def main():
    test1()
    test2()
    test3()
    test4()

def test1():
    print("========= Test 1 =========")
    rateLimiter = RateLimiter(1000, 3)
    customer1 = 123
    customer2 = 456

    # Make 8 requests alternating between two customers at a rate faster than the rate limiter allows
    for i in range(8):
        print("Customer " + str(customer1) + " Request " + str(i + 1) + " accepted (t=" + str(i * 100) + "ms)? : "
                + str(rateLimiter.allowRequest(customer1)))
        print("Customer " + str(customer2) + " Request " + str(i + 1) + " accepted (t=" + str(i * 100) + "ms)? : "
                + str(rateLimiter.allowRequest(customer2)))
        time.sleep(0.1)  # Sleep for 100 milliseconds between requests

def test2():
    print("\n========= Test 2 =========")
    rateLimiter = RateLimiter(1000, 2)

    # Test that different customers have independent limits
    for i in range(4):
        print("Customer 100 Request " + str(i + 1) + " accepted (t=" + str(i * 200) + "ms)? : "
                + str(rateLimiter.allowRequest(100)))
        print("Customer 200 Request " + str(i + 1) + " accepted (t=" + str(i * 200) + "ms)? : "
                + str(rateLimiter.allowRequest(200)))
        time.sleep(0.2)

def test3():
    print("\n========= Test 3 =========")
    rateLimiter = RateLimiter(1000, 2)
    customerId = 456

    # Fill up the rate limit
    print("Filling up rate limit:")
    for i in range(4):
        print("Customer " + str(customerId) + " Request " + str(i + 1) + " accepted (t=0ms)? : "
                + str(rateLimiter.allowRequest(customerId)))

    # Wait for time window to expire
    print("\nWaiting for time window to expire (1.1 seconds)...")
    time.sleep(1.1)

    # Try requests again - should be allowed after window expiration
    print("After time window expiration:")
    for i in range(3):
        print("Customer " + str(customerId) + " Request " + str(i + 5) + " accepted (t=1100ms)? : "
                + str(rateLimiter.allowRequest(customerId)))

def test4():
    print("\n========= Test 4 =========")
    rateLimiter = RateLimiter(1000, 2)  # 2 requests per 1000ms window

    customer1 = 101
    customer2 = 202
    customer3 = 303

    # Initial simultaneous requests
    print("Customer " + str(customer1) + " Request 1 accepted (t=0ms)? : " + str(rateLimiter.allowRequest(customer1)))
    print("Customer " + str(customer2) + " Request 1 accepted (t=0ms)? : " + str(rateLimiter.allowRequest(customer2)))

    time.sleep(0.1)  # Wait 100ms

    # Customer2 makes consecutive requests, Customer1 also tries
    print("Customer " + str(customer2) + " Request 2 accepted (t=100ms)? : " + str(rateLimiter.allowRequest(customer2)))
    print("Customer " + str(customer1) + " Request 2 accepted (t=100ms)? : " + str(rateLimiter.allowRequest(customer1)))

    time.sleep(0.1)  # Wait 100ms

    # Customer2 continues consecutive requests, Customer3 joins
    print("Customer " + str(customer2) + " Request 3 accepted (t=200ms)? : " + str(rateLimiter.allowRequest(customer2)))
    print("Customer " + str(customer3) + " Request 1 accepted (t=200ms)? : " + str(rateLimiter.allowRequest(customer3)))

    time.sleep(0.1)  # Wait 100ms

    # All customers try to make requests - some should fail due to rate limiting
    print("Customer " + str(customer2) + " Request 4 accepted (t=300ms)? : " + str(rateLimiter.allowRequest(customer2)))
    print("Customer " + str(customer1) + " Request 3 accepted (t=300ms)? : " + str(rateLimiter.allowRequest(customer1)))
    print("Customer " + str(customer3) + " Request 2 accepted (t=300ms)? : " + str(rateLimiter.allowRequest(customer3)))

    time.sleep(0.2)  # Wait 200ms

    # Customer3 tries multiple consecutive requests
    print("Customer " + str(customer3) + " Request 3 accepted (t=500ms)? : " + str(rateLimiter.allowRequest(customer3)))
    print("Customer " + str(customer3) + " Request 4 accepted (t=500ms)? : " + str(rateLimiter.allowRequest(customer3)))

    time.sleep(0.6)  # Wait 600ms - total elapsed = 1100ms

    # Window should have reset for all customers
    print("Customer " + str(customer1) + " Request 4 accepted (t=1100ms)? : " + str(rateLimiter.allowRequest(customer1)))
    print("Customer " + str(customer2) + " Request 5 accepted (t=1100ms)? : " + str(rateLimiter.allowRequest(customer2)))
    print("Customer " + str(customer3) + " Request 5 accepted (t=1100ms)? : " + str(rateLimiter.allowRequest(customer3)))
    print("Customer " + str(customer1) + " Request 5 accepted (t=1100ms)? : " + str(rateLimiter.allowRequest(customer1)))
    print("Customer " + str(customer1) + " Request 6 accepted (t=1100ms)? : " + str(rateLimiter.allowRequest(customer1)))

if __name__ == "__main__":
    main()