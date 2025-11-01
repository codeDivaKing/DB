class BankingSystem:
    def __init__(self):
        # accountId -> balance
        self.balances = {}
        # accountId -> total value of transactions (sum of deposit and pay amounts)
        self.transaction_values = {}

    def create_account(self, timestamp, accountId):
        if accountId not in self.balances:
            self.balances[accountId] = 0
            self.transaction_values[accountId] = 0
            return "true"
        return "false"

    def deposit(self, timestamp, accountId, amount):
        amount = int(amount)
        self.balances[accountId] += amount
        self.transaction_values[accountId] += amount
        return str(self.balances[accountId])

    def pay(self, timestamp, accountId, amount):
        amount = int(amount)
        self.balances[accountId] -= amount
        self.transaction_values[accountId] += amount
        return str(self.balances[accountId])

    def top_activity(self, timestamp, n):
        n = int(n)
        # Sort by (-transaction_value, accountId)
        ranked = sorted(
            self.transaction_values.items(),
            key=lambda x: (-x[1], x[0])
        )
        top_n = ranked[:n]
        # Format result
        result = ",".join([f"{acc}({val})" for acc, val in top_n])
        return result


def process_queries(queries):
    bank = BankingSystem()
    results = []

    for query in queries:
        cmd = query[0]
        if cmd == "CREATE_ACCOUNT":
            results.append(bank.create_account(query[1], query[2]))
        elif cmd == "DEPOSIT":
            results.append(bank.deposit(query[1], query[2], query[3]))
        elif cmd == "PAY":
            results.append(bank.pay(query[1], query[2], query[3]))
        elif cmd == "TOP_ACTIVITY":
            results.append(bank.top_activity(query[1], query[2]))
    return results


# Example Usage
queries = [
    ["CREATE_ACCOUNT", "1", "account1"],
    ["CREATE_ACCOUNT", "2", "account2"],
    ["CREATE_ACCOUNT", "3", "account3"],
    ["DEPOSIT", "4", "account1", "2000"],
    ["DEPOSIT", "5", "account2", "3000"],
    ["DEPOSIT", "6", "account3", "4000"],
    ["TOP_ACTIVITY", "7", "3"],
    ["PAY", "8", "account1", "1500"],
    ["PAY", "9", "account2", "250"],
    ["DEPOSIT", "10", "account3", "250"],
    ["TOP_ACTIVITY", "11", "3"]
]

print(process_queries(queries))
