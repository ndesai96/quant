from datetime import datetime, timedelta
import io
import requests
import pandas as pd
import boto3
from decimal import Decimal
import argparse
from cboe import get_cboe_data, write_to_dynamodb

# Run with:
# poetry run python -m scripts.cboe --dry-run
# poetry run python -m scripts.cboe

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backfill CBOE futures data to DynamoDB")
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Print actions without executing writes."
    )
    
    args = parser.parse_args()

    start_date = datetime(2025, 9, 1)
    end_date = datetime(2025, 9, 2)
    backfill(start_date, end_date, dry_run=args.dry_run)