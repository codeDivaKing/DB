def timer(seconds):
    # Units in descending order
    units = [
        ("months", 30 * 24 * 60 * 60),  # 30 days
        ("weeks", 7 * 24 * 60 * 60),
        ("days", 24 * 60 * 60),
        ("hours", 60 * 60),
        ("minutes", 60),
        ("seconds", 1)
    ]

    def helper(sec, idx):
        # Base case: always include seconds, even if zero
        if idx == len(units) - 1:
            return [f"{sec} seconds"]

        name, size = units[idx]
        count = sec // size
        remainder = sec % size

        parts = []

        # Only include unit if count > 0
        if count > 0:
            parts.append(f"{count} {name}")

        # Recurse into next unit
        parts.extend(helper(remainder, idx + 1))

        # If this is not seconds and the next part is zero seconds
        # it's allowed (0 seconds always shown)
        # Zero *other* units are never shown — already handled above

        return parts

    # Start recursion at first unit
    parts = helper(seconds, 0)

    # Join with commas
    return ", ".join(parts)

print(timer(55))
print(timer(65))
print(timer(300))
print(timer(3723))
print(timer(86405))
print(timer(200000))
print(timer(900000))
print(timer(2500000))
print(timer(3805000))
print(timer(10000000))
