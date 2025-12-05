def has_duplicate(ids):
    seen = set()
    for x in ids:
        if x in seen:
            return True
        seen.add(x)
    return False

def has_duplicate_in_window(ids, K):
    window = set()
    
    for i in ids:
        if len(window) == K:
            window.remove(ids[i - K])
        if i in window:
            return True
        window.add(i)
    return False
            

def is_series(ids, T):
    ids.sort()

    for i in range(len(ids) - 1):
        if ids[i+1] - ids[i] <= T:
            return True
    return False
        