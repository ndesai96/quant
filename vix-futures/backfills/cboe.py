from datetime import datetime, timedelta
import io
import requests
import pandas as pd
import boto3
from decimal import Decimal
from config import CBOE_URL, TABLE_NAME, REGION
import argparse

# Run with:
# poetry run python -m backfills.cboe --dry-run
# poetry run python -m backfills.cboe

def backfill(start_date: datetime, end_date: datetime, dry_run: bool = False):
    date = start_date
    while date <= end_date:
        dateString = date.strftime('%Y-%m-%d')

        # Skip non-trading days
        if date.weekday() >= 5:
            print(f"Skipping non-trading day {dateString}")
            date += timedelta(days=1)
            continue

        print(f"Fetching futures data for {dateString}")
        
        data = get_cboe_data(date)
        if data.empty:
            print(f"No data for {dateString}")
            date += timedelta(days=1)
            continue
        
        if dry_run:
            print(f"Would have written {len(data)} items to DynamoDB for {dateString}")
        else:
            count = write_to_dynamodb(data, dateString)
            print(f"Wrote {count} items to DynamoDB for {dateString}")
        
        date += timedelta(days=1)

def get_cboe_data(date: datetime) -> pd.DataFrame:
    dateString = date.strftime("%Y-%m-%d")
    
    url = CBOE_URL.format(date=dateString)

    try:
        response = requests.get(url)
    except Exception as e:
        print(f"Error getting data for {dateString}: {e}")
        return pd.DataFrame()

    if response.status_code != 200:
        print(f"Error getting data for {dateString}: {response.status_code}")
        return pd.DataFrame()
    
    return pd.read_csv(io.StringIO(response.content.decode("utf-8")))

def write_to_dynamodb(data: pd.DataFrame, date: str)-> int:
    dynamodb = boto3.resource('dynamodb', region_name=REGION)

    table = dynamodb.Table(TABLE_NAME)
    count = 0

    if data.empty:
        print(f"No data for {date}")
        return count
    
    for index, row in data.iterrows():
        price = Decimal(str(row['Price']))

        item = {
            'product': row['Product'],
            'symbol': row['Symbol'],
            'expiration_date': row['Expiration Date'],
            'price': price,
            'date_symbol': date + '_' + row['Symbol'],
            'date': date,
        }

        try:
            table.put_item(Item=item)
        except Exception as e:
            print(f"Error putting item {item['date_symbol']} to DynamoDB: {e}")
            continue

        count += 1

    return count

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backfill CBOE futures data to DynamoDB")
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Print actions without executing writes."
    )
    
    args = parser.parse_args()

    start_date = datetime(2025, 9, 1)
    end_date = datetime(2025, 9, 30)
    backfill(start_date, end_date, dry_run=args.dry_run)