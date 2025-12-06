from boto3.dynamodb.conditions import Key
from datetime import datetime
from config import REGION, TABLE_NAME, VIX_CENTRAL_URL, FUTURES_MONTH_CODES
import boto3
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from datetime import timedelta

def get_historical_futures_data(start_date: datetime, end_date: datetime) -> list:
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    table = dynamodb.Table(TABLE_NAME)

    response = table.query(
        KeyConditionExpression=Key('product').eq('VX') & Key('date_symbol').between(
            start_date.strftime('%Y-%m-%d'), 
            end_date.strftime('%Y-%m-%d')
        )
    )

    data = response['Items']
    historical = defaultdict(list)

    for item in data:
        future = {
            'price': float(item['price']),
            'symbol': item['symbol'],
            'expiration_date': item['expiration_date']
        }
        historical[item['date']].append(future)
    
    return historical

import requests

def get_realtime_futures_data():
    url = VIX_CENTRAL_URL + 'ajax_update'
    headers = {
        "Referer": VIX_CENTRAL_URL,
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        months = data[0] # (e.g., "Dec", "Jan")
        prices = data[2] # (e.g., "12.34", "56.78")

        now = datetime.now()
        year = now.year
        
        month_num = datetime.strptime(months[0], "%b").month
        if month_num < now.month:
             year += 1
        
        futures_data = []

        for month, price in zip(months, prices):
            if month and price:
                prev_month_num = month_num
                month_num = datetime.strptime(month, "%b").month
                
                # January < December -> new year
                if month_num < prev_month_num:
                    year += 1
                                
                futures_data.append({
                    "price": float(price),
                    "symbol": get_futures_symbol(month, year),
                    "expiration_date": calculate_expiration_date(month_num, year)
                })
                
        return futures_data
        
    except Exception as e:
        print(f"Error fetching real-time data: {e}")
        return []

# January 2026 -> VX/F6
def get_futures_symbol(month: str, year: int) -> str:
    month_code = FUTURES_MONTH_CODES.get(month)
    if not month_code:
        raise ValueError(f"Invalid month: {month}")
    return f"VX/{month_code}{year % 10}"

# January 2026 -> expiration_date = 2026-01-14
def calculate_expiration_date(month: int, year: int) -> str:
    """
    Calculates the VIX futures expiration date for a given contract month.
    Rule: Wednesday that is 30 days prior to the 3rd Friday of the FOLLOWING month.
    """

    # 1. Get the 'following' month
    following_month_date = datetime(year, month, 1) + relativedelta(months=1)
        
    # 2. Find the 3rd Friday of that following month
    # Start at the 1st day
    day = following_month_date.replace(day=1)
    # Move to the first Friday (weekday 4)
    while day.weekday() != 4:
        day += timedelta(days=1)
    # Add 2 weeks to get the 3rd Friday
    third_friday = day + timedelta(weeks=2)
    
    # 3. Subtract 30 days to get VIX expiration
    return (third_friday - timedelta(days=30)).strftime('%Y-%m-%d')