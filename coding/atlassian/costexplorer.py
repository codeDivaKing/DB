from datetime import date, timedelta
from enum import Enum
from collections import defaultdict
from dataclasses import dataclass

class Plan(Enum):
    BASIC = 1
    STANDARD = 2
    PREMIUM = 3

@dataclass
class SUBSCRIPTION:
    start: date
    end: date | None      # None = still active
    plan: Plan

class CostExplorer:
    def __init__(self):
        self.monthly_prices = {
            Plan.BASIC: 10.0,
            Plan.STANDARD: 20.0,
            Plan.PREMIUM: 35.0
        }

        # member → list of SUBSCRIPTION intervals
        self.member_cost = defaultdict(list)

    def addEvent(self, events: list):
        for memberid, subscription in events:
            self.member_cost[memberid].append(subscription)

    # -----------------------------------------------
    # Helper: iterate through each day subscription is active
    # -----------------------------------------------
    def _iterate_active_days(self, start, end):
        """Yield each active day between start and end inclusive."""
        cur = start
        while cur <= end:
            yield cur
            cur += timedelta(days=1)

    # -----------------------------------------------
    # Monthly cost (12 values) with daily prorating
    # -----------------------------------------------
    def get_monthly_cost(self, memberid: int, year: int) -> list[float]:
        months = [0.0] * 12
        subs = self.member_cost[memberid]

        if not subs:
            return months

        year_start = date(year, 1, 1)
        year_end = date(year, 12, 31)

        for sub in subs:
            sub_start = max(sub.start, year_start)   # clip interval to year
            sub_end = min(sub.end or year_end, year_end)

            if sub_start > sub_end:
                continue

            price = self.monthly_prices[sub.plan]

            # Add cost day by day
            for day in self._iterate_active_days(sub_start, sub_end):
                month_index = day.month - 1
                days_in_month = (date(day.year, day.month % 12 + 1, 1) - timedelta(days=1)).day \
                                if day.month != 12 else 31

                daily_rate = price / days_in_month
                months[month_index] += daily_rate

        # round for cleaner statements (optional)
        return [round(m, 2) for m in months]

    # -----------------------------------------------
    # Yearly cost = sum of each month cost
    # -----------------------------------------------
    def get_yearly_cost(self, memberid: int, year: int) -> float:
        return sum(self.get_monthly_cost(memberid, year))

# -----------------------------------------------------------
#                     TEST HARNESS
# -----------------------------------------------------------

ce = CostExplorer()

# Add sample subscriptions
events = [
    # member 1 BASIC from Jan–Mar 2025
    (1, SUBSCRIPTION(start=date(2025, 1, 1), end=date(2025, 3, 31), plan=Plan.BASIC)),

    # member 1 PREMIUM Apr–Jun 2025
    (1, SUBSCRIPTION(start=date(2025, 4, 1), end=date(2025, 6, 30), plan=Plan.PREMIUM)),

    # member 1 STANDARD July–end of year (ongoing)
    (1, SUBSCRIPTION(start=date(2025, 7, 1), end=None, plan=Plan.STANDARD)),
]

ce.addEvent(events)

print("Monthly cost for member 1 in 2025:")
print(ce.get_monthly_cost(1, 2025))   # placeholder output

print("\nYearly cost for member 1 in 2025:")
print(ce.get_yearly_cost(1, 2025))    # placeholder output

print("\nMonthly cost for member with no subscription (id=99):")
print(ce.get_monthly_cost(99, 2025))
