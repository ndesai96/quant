from datetime import datetime, timedelta
import boto3
from config import REGION, TABLE_NAME
from boto3.dynamodb.conditions import Key
import json

# Run with:
# poetry run python -m handlers.futures

def lambda_handler(event, context):
    query_params = event.get('queryStringParameters')

    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()

    if query_params:
        try:
            start_date = datetime.strptime(query_params.get('start_date'), '%Y-%m-%d')
            end_date = datetime.strptime(query_params.get('end_date'), '%Y-%m-%d')

            if start_date and end_date and end_date < start_date:
                return {
                    'statusCode': 400,
                    'body': json.dumps('Error: end_date cannot be before start_date')
                }
        except ValueError:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid date format. Use YYYY-MM-DD.'})
            }
    
    response_data = {
        'historical': get_historical_data(start_date, end_date)
    }

    return {
        'statusCode': 200,
        'body': json.dumps(response_data)
    }
    
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

if __name__ == '__main__':
    event = {
        'queryStringParameters': {
            'start_date': '2025-11-01',
            'end_date': '2025-11-04'
        }
    }
    response = lambda_handler(event, None)
    print(response)
