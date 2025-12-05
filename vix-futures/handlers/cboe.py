import json
from datetime import datetime
from cboe import get_cboe_data, write_to_dynamodb

# Run with:
# poetry run python -m handlers.cboe

def lambda_handler(event, context):
    today = datetime.now()
    data = get_cboe_data(today)
    count = write_to_dynamodb(data, today.strftime('%Y-%m-%d'))
    
    if count == 0:
        message = 'No data found for ' + today.strftime('%Y-%m-%d')
    else:
        message = f'Successfully wrote {count} items to DynamoDB'
    
    return {
        'statusCode': 200,
        'body': json.dumps(message)
    }

if __name__ == '__main__':
    response = lambda_handler(None, None)
    print(response)
