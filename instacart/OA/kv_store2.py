import bisect
import copy
from collections import defaultdict

def solution(queries):
    # ---------- global state ----------
    store = defaultdict(lambda: defaultdict(list))  # key → field → [(timestamp, value[, expire])]
    backups = {}

    results = []

    for q in queries:
        cmd = q[0]

        # ---------- LEVEL 1 ----------
        if cmd == "SET":
            # ["SET", key, field, value]
            _, key, field, value = q
            store[key][field] = [(0, value)]
            results.append("true")

        elif cmd == "GET":
            # ["GET", key, field]
            _, key, field = q
            results.append(store.get(key, {}).get(field, [(0, "")])[-1][1])

        elif cmd == "COMPARE_AND_UPDATE":
            # ["COMPARE_AND_UPDATE", key, field, old_val, new_val]
            _, key, field, old_val, new_val = q
            if store.get(key, {}).get(field, [(0, "")])[-1][1] != old_val:
                results.append("false")
            else:
                store[key][field] = [(0, new_val)]
                results.append("true")

        elif cmd == "COMPARE_AND_DELETE":
            # ["COMPARE_AND_DELETE", key, field, old_val]
            _, key, field, old_val = q
            if store.get(key, {}).get(field, [(0, "")])[-1][1] != old_val:
                results.append("false")
            else:
                del store[key][field]
                if not store[key]:
                    del store[key]
                results.append("true")

        # ---------- LEVEL 2 ----------
        elif cmd == "SET_TS":
            # ["SET_TS", timestamp, key, field, value]
            _, ts, key, field, value = q
            ts = int(ts)
            store[key][field].append((ts, value))
            results.append("true")

        elif cmd == "FIND":
            # ["FIND", timestamp, key, field]
            _, ts, key, field = q
            ts = int(ts)
            arr = store.get(key, {}).get(field, [])
            arr.sort()  # ensure order if not guaranteed
            i = bisect.bisect_right(arr, (ts,)) - 1
            results.append(arr[i][1] if i >= 0 else "")

        elif cmd == "SCAN":
            # ["SCAN", timestamp, key]
            _, ts, key = q
            ts = int(ts)
            if key not in store:
                results.append([])
                continue
            arr = []
            for f in sorted(store[key]):
                vals = store[key][f]
                vals.sort()
                i = bisect.bisect_right(vals, (ts,)) - 1
                if i >= 0:
                    arr.append((f, vals[i][1]))
            results.append(arr)

        elif cmd == "SCAN_BY_PREFIX":
            # ["SCAN_BY_PREFIX", timestamp, key, prefix]
            _, ts, key, prefix = q
            ts = int(ts)
            if key not in store:
                results.append([])
                continue
            arr = []
            for f in sorted(store[key]):
                if f.startswith(prefix):
                    vals = store[key][f]
                    vals.sort()
                    i = bisect.bisect_right(vals, (ts,)) - 1
                    if i >= 0:
                        arr.append((f, vals[i][1]))
            results.append(arr)

        # ---------- LEVEL 3 ----------
        elif cmd == "SET_TTL":
            # ["SET_TTL", timestamp, key, field, value, ttl]
            _, ts, key, field, value, ttl = q
            ts, ttl = int(ts), int(ttl)
            expire = ts + ttl
            store[key][field].append((ts, value, expire))
            results.append("true")

        elif cmd == "FIND_TTL":
            # ["FIND_TTL", timestamp, key, field]
            _, ts, key, field = q
            ts = int(ts)
            arr = store.get(key, {}).get(field, [])
            arr.sort()
            i = bisect.bisect_right(arr, (ts,)) - 1
            if i < 0:
                results.append("")
            else:
                t, v, exp = arr[i]
                results.append("" if ts >= exp else v)

        elif cmd == "COMPARE_AND_UPDATE_TTL":
            # ["COMPARE_AND_UPDATE_TTL", timestamp, key, field, old_val, new_val, ttl]
            _, ts, key, field, old_val, new_val, ttl = q
            ts, ttl = int(ts), int(ttl)
            arr = store.get(key, {}).get(field, [])
            arr.sort()
            i = bisect.bisect_right(arr, (ts,)) - 1
            if i < 0:
                results.append("false")
                continue
            t, v, exp = arr[i]
            if ts >= exp or v != old_val:
                results.append("false")
            else:
                exp_time = ts + ttl
                store[key][field].append((ts, new_val, exp_time))
                results.append("true")

        # ---------- LEVEL 4 ----------
        elif cmd == "BACKUP":
            # ["BACKUP", timestamp]
            _, ts = q
            ts = int(ts)
            backups[ts] = copy.deepcopy(store)
            results.append("true")

        elif cmd == "RESTORE":
            # ["RESTORE", timestamp]
            _, ts = q
            ts = int(ts)
            if ts not in backups:
                results.append("false")
            else:
                store = copy.deepcopy(backups[ts])
                results.append("true")

        elif cmd == "GET_AT":
            # ["GET_AT", timestamp, key, field]
            _, ts, key, field = q
            ts = int(ts)
            arr = store.get(key, {}).get(field, [])
            arr.sort()
            i = bisect.bisect_right(arr, (ts,)) - 1
            results.append(arr[i][1] if i >= 0 else "")

        else:
            results.append("")

    return results
