from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

FUTURES_MONTH_CODES = {
    1: 'F', 2: 'G', 3: 'H', 4: 'J', 5: 'K', 6: 'M',
    7: 'N', 8: 'Q', 9: 'U', 10: 'V', 11: 'X', 12: 'Z'
}

class Future:
    def __init__(self, month: int, year: int):
        self.month = month
        self.year = year

    def get_ticker(self) -> str:
        return f"VX{FUTURES_MONTH_CODES[self.month]}{str(self.year)[-2:]}.CBO"

    def get_expiry(self) -> datetime:
        """
        Calculates the VIX futures expiration date for a given contract month.
        Rule: Wednesday that is 30 days prior to the 3rd Friday of the FOLLOWING month.
        """

        # 1. Get the 'following' month
        following_month_date = datetime(self.year, self.month, 1) + relativedelta(months=1)
        
        # 2. Find the 3rd Friday of that following month
        # Start at the 1st day
        day = following_month_date.replace(day=1)
        # Move to the first Friday (weekday 4)
        while day.weekday() != 4:
            day += timedelta(days=1)
        # Add 2 weeks to get the 3rd Friday
        third_friday = day + timedelta(weeks=2)
        
        # 3. Subtract 30 days to get VIX expiration
        return third_friday - timedelta(days=30)

def build_futures(month: int, year: int, num=4) -> list[Future]:
    futures = []
    future_date = datetime(year, month, 1)

    for _ in range(num):
        futures.append(Future(future_date.month, future_date.year))
        future_date += relativedelta(months=1)
    
    return futures

def get_tickers(futures: list[Future]) -> list[str]:
    return [future.get_ticker() for future in futures]


    