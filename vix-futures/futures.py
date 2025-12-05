from boto3.dynamodb.conditions import Key
from datetime import datetime
from config import REGION, TABLE_NAME
import boto3

def get_historical_data(start_date: datetime, end_date: datetime) -> list:
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    table = dynamodb.Table(TABLE_NAME)

    response = table.query(
        KeyConditionExpression=Key('product').eq('VX') & Key('date_symbol').between(
            start_date.strftime('%Y-%m-%d'), 
            end_date.strftime('%Y-%m-%d')
        )
    )

    data = response['Items']
    for item in data:
        item['price'] = float(item['price'])
    
    return data