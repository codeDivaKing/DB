from sortedcontainers import SortedDict

class WeightedCache:
    """
    Cache with (key -> (value, weight)).
    When total weight exceeds capacity, evict the largest-weight items.
    """

    def __init__(self, capacity_weight: int):
        self.capacity = capacity_weight
        self.total_weight = 0

        self.store = {}            # key -> (value, weight)
        self.weight_map = SortedDict()   # weight -> set of keys

    def _add_to_weight_map(self, weight, key):
        if weight not in self.weight_map:
            self.weight_map[weight] = set()
        self.weight_map[weight].add(key)

    def _remove_from_weight_map(self, weight, key):
        bucket = self.weight_map[weight]
        bucket.remove(key)
        if not bucket:
            del self.weight_map[weight]

    def get(self, key):
        if key not in self.store:
            return None 
        return self.store[key][0]

    def put(self, key, value, weight):
        # Remove old weight if key exists
        if key in self.store:
            _, old_weight = self.store[key]
            self._remove_from_weight_map(old_weight, key)
            self.total_weight -= old_weight

        # Insert new
        self.store[key] = (value, weight)
        self._add_to_weight_map(weight, key)
        self.total_weight += weight

        # Evict largest weight until under capacity
        while self.total_weight > self.capacity:
            max_weight, keys = self.weight_map.peekitem(-1)
            evict_key = keys.pop()  # arbitrary key in this bucket

            if not keys:
                del self.weight_map[max_weight]

            del self.store[evict_key]
            self.total_weight -= max_weight


cache = WeightedCache(10)

cache.put("a", "AAA", 3)
cache.put("b", "BBB", 4)
cache.put("c", "CCC", 7)  # exceeds cap → evict heaviest = "c"

print(cache.store)
# Expect: "a", "b"
