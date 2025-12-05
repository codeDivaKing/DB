

class RateLimiter:
    def __init__(self, limit: int, window_size: int):
        """
        limit: maximum number of requests allowed in any sliding window
        window_size: size of the sliding window in seconds
        """
        self.limit = limit
        self.window_size = window_size
        self.logs = defaultdict(deque)

    def allow(self, user_id: str, timestamp: int) -> bool:
        """
        Returns True if this request is allowed under the rate limit
        for this user, otherwise returns False.

        Slide the window based on 'timestamp'.
        """
        q = self.logs[user_id]

        while q and q[0] <= timestamp - self.window_size:
            q.popleft()
        
        if len(q) < self.limit:
            q.append(timestamp)
            return True
        return False
                

def gc(self, current_ts):
    to_delete = []
    for user, q in self.logs.items():
        while q and q[0] <= current_ts - self.window:
            q.popleft()
        if not q:
            to_delete.append(user)
    for user in to_delete:
        del self.logs[user]



from collections import defaultdict, deque

class RpcRateLimiter:
    def __init__(self, default_limit_per_minute: int):
        self.default_limit = default_limit_per_minute
        self.window = 60
        self.client_quota = {}  # client_id -> custom limit
        self.logs = defaultdict(deque)  # (client_id, method) -> timestamps

    def set_client_quota(self, client_id: str, limit_per_minute: int):
        self.client_quota[client_id] = limit_per_minute

    def _get_quota(self, client_id: str):
        return self.client_quota.get(client_id, self.default_limit)

    def allow(self, request):
        key = (request.client_id, request.method_name)
        quota = self._get_quota(request.client_id)
        q = self.logs[key]

        # evict old logs
        while q and q[0] <= request.timestamp - self.window:
            q.popleft()

        # check quota
        if len(q) < quota:
            q.append(request.timestamp)
            return True
        return False

