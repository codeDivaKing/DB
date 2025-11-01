MILLISECONDS_IN_1_DAY = 24 * 60 * 60 * 1000  # 86400000

def solution(queries):
    # State
    balances = {}             # accountId -> current balance
    transaction_values = {}   # accountId -> total transaction value
    transfers = {}            # transferId -> details
    transfer_count = 0        # counter for unique transfer ids

    results = []

    for q in queries:
        cmd = q[0]

        # ---------- LEVEL 1 ----------
        if cmd == "CREATE_ACCOUNT":
            _, timestamp, accountId = q
            if accountId not in balances:
                balances[accountId] = 0
                transaction_values[accountId] = 0
                results.append("true")
            else:
                results.append("false")

        elif cmd == "DEPOSIT":
            _, timestamp, accountId, amount = q
            amount = int(amount)
            if accountId not in balances:
                results.append("")
                continue
            balances[accountId] += amount
            transaction_values[accountId] += amount
            results.append(str(balances[accountId]))

        elif cmd == "PAY":
            _, timestamp, accountId, amount = q
            amount = int(amount)
            if accountId not in balances:
                results.append("")
                continue
            balances[accountId] -= amount
            transaction_values[accountId] += amount
            results.append(str(balances[accountId]))

        # ---------- LEVEL 2 ----------
        elif cmd == "TOP_ACTIVITY":
            _, timestamp, n = q
            n = int(n)
            ranked = sorted(transaction_values.items(), key=lambda x: (-x[1], x[0]))
            top_n = ranked[:n]
            formatted = ",".join(f"{acc}({val})" for acc, val in top_n)
            results.append(formatted)

        # ---------- LEVEL 3 ----------
        elif cmd == "TRANSFER":
            _, timestamp, src, tgt, amount = q
            ts = int(timestamp)
            amount = int(amount)

            if src == tgt or src not in balances or tgt not in balances or balances[src] < amount:
                results.append("")
                continue

            balances[src] -= amount
            transfer_count += 1
            transfer_id = f"transfer{transfer_count}"
            transfers[transfer_id] = {
                "source": src,
                "target": tgt,
                "amount": amount,
                "start": ts,
                "accepted": False,
                "completed": False
            }
            results.append(transfer_id)

        elif cmd == "ACCEPT_TRANSFER":
            _, timestamp, accountId, transferId = q
            ts = int(timestamp)

            if transferId not in transfers:
                results.append("false")
                continue

            transfer = transfers[transferId]
            src, tgt, amt = transfer["source"], transfer["target"], transfer["amount"]

            # Expired
            if ts - transfer["start"] >= MILLISECONDS_IN_1_DAY:
                if not transfer["completed"]:
                    balances[src] += amt
                    transfer["completed"] = True
                results.append("false")
                continue

            # Already processed
            if transfer["completed"]:
                results.append("false")
                continue

            # Wrong target
            if tgt != accountId:
                results.append("false")
                continue

            # Success
            balances[tgt] += amt
            transaction_values[src] += amt
            transaction_values[tgt] += amt
            transfer["accepted"] = True
            transfer["completed"] = True
            results.append("true")

        else:
            results.append("")

    return results
