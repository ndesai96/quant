from datetime import datetime, timedelta
import boto3
from config import REGION, TABLE_NAME
from boto3.dynamodb.conditions import Key
import json
from futures import get_historical_futures_data, get_realtime_futures_data
from vix import get_vix_data

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
        'vix': get_vix_data(),
        'futures': {
            'historical': get_historical_futures_data(start_date, end_date),
            'realtime': get_realtime_futures_data()
        }
    }

    return {
        'statusCode': 200,
        'body': json.dumps(response_data)
    }
    
if __name__ == '__main__':
    today = datetime.now()
    start_date = today - timedelta(days=3)
    end_date = today

    event = {
        'queryStringParameters': {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        }
    }
    response = lambda_handler(event, None)
    print(response)
