import requests
import io
import boto3
from decimal import Decimal
from config import CBOE_URL, TABLE_NAME, REGION
import pandas as pd

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