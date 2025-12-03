from sortedcontainers import SortedDict

class StockPrice:

    def __init__(self):
        self.latest = 0
        self.time_price = {}
        self.price_frequency = SortedDict()

    def update(self, timestamp: int, price: int) -> None:
        self.latest = max(self.latest, timestamp)
        if timestamp in self.time_price:
            old_price = self.time_price[timestamp]
            self.price_frequency[old_price] -= 1
            if self.price_frequency[old_price] == 0:
                del self.price_frequency[old_price]
            
        self.time_price[timestamp] = price
        if price in self.price_frequency:
            self.price_frequency[price] += 1
        else:
            self.price_frequency[price] = 1

    def current(self) -> int:
        return self.time_price[self.latest]

    def maximum(self) -> int:
        return self.price_frequency.peekitem(-1)[0]

    def minimum(self) -> int:
        return self.price_frequency.peekitem(0)[0]


obj = StockPrice()
obj.update(1,10)
obj.update(2,5)
obj.update(3,15)
obj.update(4,20)
obj.update(5,10)
print(obj.current())
print(obj.maximum())
print(obj.minimum())

class priceCommidity:
    def __init__(self):
        self.snapshots = []

    def update(self, timestamp: int, price: int):
        if self.snapshots:
            new_snap = SortedDict(self.snapshorts[-1])
        else:
            new_snap = SortedDict()

        new_snap[timestamp] = price
        self.snapshots.append(new_snap)
    
    def maxPrice(self, timestamp: int, checkpoint: int):
        if checkpoint >= len(self.snapshots):
            return None
        
        snap = self.snapshots[checkpoint]
        # find all timestamps <= T
        idx = snap.bisect_right(timestamp)
        if idx == 0:
            return None
        
        return max(snap.values()[:idx])

# Operation	Time Complexity	Explanation
# update	⭐ O(N)	Copy SortedDict (O(N)) + insert (O(log N))
# maxPrice	⭐ O(K)	K = #timestamps ≤ T (prefix scan)
# memory	❗ O(N²)	Because each checkpoint stores a full copy


# segment Tree
from bisect import bisect_right

class Node:
    __slots__ = ("left", "right", "value")
    def __init__(self, left=None, right=None, value=0):
        self.left = left
        self.right = right
        self.value = value


class CommodityPriceHistory:
    def __init__(self):
        self.timestamps = []       # sorted list of distinct timestamps
        self.ts_to_idx = {}        # timestamp -> compressed index
        self.roots = [None]        # root[0] = empty version

    # ----------------------------------------
    # Persistent segment tree update
    # ----------------------------------------
    def _update(self, prev, l, r, idx, price):
        if l == r:
            return Node(value=price)

        mid = (l + r) // 2

        if idx <= mid:
            left = self._update(prev.left if prev else None, l, mid, idx, price)
            right = prev.right if prev else None
        else:
            left = prev.left if prev else None
            right = self._update(prev.right if prev else None, mid+1, r, idx, price)

        val = max(left.value if left else 0,
                  right.value if right else 0)
        return Node(left, right, val)

    # ----------------------------------------
    # Persistent segment tree range max query
    # ----------------------------------------
    def _query(self, node, l, r, ql, qr):
        if not node or qr < l or r < ql:
            return 0
        if ql <= l and r <= qr:
            return node.value

        mid = (l + r) // 2
        return max(
            self._query(node.left,  l, mid, ql, qr),
            self._query(node.right, mid+1, r, ql, qr)
        )

    # ----------------------------------------
    # Public API
    # ----------------------------------------
    def update(self, timestamp, price):
        # Compress timestamp (append-only)
        if timestamp not in self.ts_to_idx:
            self.ts_to_idx[timestamp] = len(self.timestamps)
            self.timestamps.append(timestamp)
            self.timestamps.sort()  # We sort ONLY this small list of timestamps

            # Re-assign indices because sorted order changed
            for i, t in enumerate(self.timestamps):
                self.ts_to_idx[t] = i

        idx = self.ts_to_idx[timestamp]

        prev_root = self.roots[-1]
        n = len(self.timestamps)

        new_root = self._update(prev_root, 0, n-1, idx, price)
        self.roots.append(new_root)

    def maxPrice(self, T, checkpoint):
        cp = checkpoint
        if cp < 0 or cp >= len(self.roots):
            raise ValueError("invalid checkpoint")

        # find largest timestamp <= T
        pos = bisect_right(self.timestamps, T) - 1
        if pos < 0:
            return 0

        return self._query(self.roots[cp], 0, len(self.timestamps)-1, 0, pos)
