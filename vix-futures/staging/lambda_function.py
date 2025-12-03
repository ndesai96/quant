import yfinance as yf

def lambda_handler(event, context):
    vix = yf.download("^VIX", period="5d", interval="1m", progress=False, auto_adjust=True)

    return {
        'statusCode': 200,
        'body': {
            "vix": {
                "close": vix["Close"].iloc[-1].item(),
                "datetime": vix.index[-1].tz_convert('US/Central').isoformat(),
            }
        }
    }
