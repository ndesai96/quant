import yfinance as yf

def lambda_handler(event, context):
    tickers = ['^VIX', '^VIX3M', '^SKEW']
    data = yf.download(tickers, period="5d", interval="1d", progress=False, auto_adjust=True)

    # Forward fill to handle missing data for some tickers on the last day
    closes = data['Close'].ffill()

    return {
        'statusCode': 200,
        'body': {
            "vix": closes['^VIX'].iloc[-1].item(),
            "vix3m": closes['^VIX3M'].iloc[-1].item(),
            "skew": closes['^SKEW'].iloc[-1].item(),
        }
    }
