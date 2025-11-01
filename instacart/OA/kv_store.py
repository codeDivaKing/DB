# ; Level 1: 实现 set， get， 比较并更新，比较并删除四个操作
# ; level 2: 实现 扫描和用前缀扫描并排序后返回 两个功能
# ; level 3: 引入TTL，实现set w ttl，比较并更新ttl 两个功能，此处还要注意需要更新所有get的method，不能返回已经过期的值
# ; level 4: 给一个过去的时间点，返回当下时间点的值，相当于实现一个archive系统

# ; lc: 981

# ; set(key, field, value), find(key, field), findByPrefix(key, field), delete(key, field)


# ; 拓展是以上的每个操作都加入timestamp这一个parameter


# ; 进一步加上TTL,比如set at time1, time1+TTL 就会expire,那时候find,delete操作就应该是失败的


# ; 最后一部分是实现backup, restore两个操作

#level1
from collections import defaultdict

class KVStoreV1:
    def __init__(self):
        # key → field → value
        self.store = defaultdict(dict)

    def set(self, key, field, value):
        self.store[key][field] = value
        return "true"

    def get(self, key, field):
        return self.store.get(key, {}).get(field, "")

    def compare_and_update(self, key, field, old_val, new_val):
        if self.get(key, field) != old_val:
            return "false"
        self.store[key][field] = new_val
        return "true"

    def compare_and_delete(self, key, field, old_val):
        if self.get(key, field) != old_val:
            return "false"
        del self.store[key][field]
        if not self.store[key]:
            del self.store[key]
        return "true"


# Example
db = KVStoreV1()
print(db.set("user1", "name", "Alice"))              # true
print(db.get("user1", "name"))                       # Alice
print(db.compare_and_update("user1", "name", "Alice", "Bob"))  # true
print(db.get("user1", "name"))                       # Bob
print(db.compare_and_delete("user1", "name", "Bob")) # true
print(db.get("user1", "name"))                       # ""

#level 2
from collections import defaultdict
import bisect

class KVStoreV2:
    def __init__(self):
        # key → field → [(timestamp, value)]
        self.store = defaultdict(lambda: defaultdict(list))

    def set(self, timestamp, key, field, value):
        self.store[key][field].append((timestamp, value))
        return "true"

    def find(self, timestamp, key, field):
        if key not in self.store or field not in self.store[key]:
            return ""
        arr = self.store[key][field]
        i = bisect.bisect_right(arr, (timestamp, chr(255))) - 1
        if i < 0:
            return ""
        return arr[i][1]

    def scan(self, timestamp, key):
        if key not in self.store:
            return []
        result = []
        for f in sorted(self.store[key]):
            val = self.find(timestamp, key, f)
            if val != "":
                result.append((f, val))
        return result

    def scan_by_prefix(self, timestamp, key, prefix):
        if key not in self.store:
            return []
        result = []
        for f in sorted(self.store[key]):
            if f.startswith(prefix):
                val = self.find(timestamp, key, f)
                if val != "":
                    result.append((f, val))
        return result


# Example
db = KVStoreV2()
db.set(1, "k", "a", "v1")
db.set(2, "k", "ab", "v2")
db.set(3, "k", "b", "v3")
print(db.scan(4, "k"))              # [('a','v1'), ('ab','v2'), ('b','v3')]
print(db.scan_by_prefix(4, "k", "a"))  # [('a','v1'), ('ab','v2')]

#level 3
from collections import defaultdict
import bisect

class KVStoreV3:
    def __init__(self):
        # key → field → [(timestamp, value, expire_time)]
        self.store = defaultdict(lambda: defaultdict(list))

    def set_with_ttl(self, timestamp, key, field, value, ttl):
        expire_time = timestamp + ttl
        self.store[key][field].append((timestamp, value, expire_time))
        return "true"

    def find(self, timestamp, key, field):
        if key not in self.store or field not in self.store[key]:
            return ""
        arr = self.store[key][field]
        i = bisect.bisect_right(arr, (timestamp, chr(255), float("inf"))) - 1
        if i < 0:
            return ""
        t, val, exp = arr[i]
        if exp is not None and timestamp >= exp:
            return ""  # expired
        return val

    def compare_and_update_ttl(self, timestamp, key, field, old_val, new_val, ttl):
        current = self.find(timestamp, key, field)
        if current == "" or current != old_val:
            return "false"
        expire_time = timestamp + ttl
        self.store[key][field].append((timestamp, new_val, expire_time))
        return "true"



import copy
from collections import defaultdict
import bisect

#level4
class KVStoreV4:
    def __init__(self):
        self.store = defaultdict(lambda: defaultdict(list))
        self.backups = {}

    def set(self, timestamp, key, field, value):
        self.store[key][field].append((timestamp, value))
        return "true"

    def find(self, timestamp, key, field):
        if key not in self.store or field not in self.store[key]:
            return ""
        arr = self.store[key][field]
        i = bisect.bisect_right(arr, (timestamp, chr(255))) - 1
        return arr[i][1] if i >= 0 else ""

    def backup(self, timestamp):
        self.backups[timestamp] = copy.deepcopy(self.store)
        return "true"

    def restore(self, timestamp):
        if timestamp not in self.backups:
            return "false"
        self.store = copy.deepcopy(self.backups[timestamp])
        return "true"

    def get_at(self, historical_time, key, field):
        return self.find(historical_time, key, field)


# Example
db = KVStoreV4()
db.set(1, "k", "field", "old")
db.backup(2)
db.set(3, "k", "field", "new")
print(db.find(4, "k", "field"))   # new
db.restore(2)
print(db.find(4, "k", "field"))   # old
print(db.get_at(1, "k", "field")) # old
