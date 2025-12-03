import yfinance as yf

def lambda_handler(event, context):
    vix_spot, vix_sma = get_history('^VIX', 20)

    signal = "STABLE"
    if vix_spot > (vix_sma * 1.10):
        signal = "SPIKING"
    elif vix_spot < (vix_sma * 0.90):
        signal = "CRUSHED"
    
    return {
        'statusCode': 200,
        'body': {
            'vix': {
                'spot': vix_spot,
                'sma': vix_sma,
                'diff_pct': ((vix_spot - vix_sma) / vix_sma) * 100,
                'signal': signal
            }
        }
    }


def get_history(ticker, window=20) -> tuple[float, float]:
    data = yf.download(ticker, period="6mo", interval="1d", progress=False, auto_adjust=True)
    spot = data['Close'].ffill().iloc[-1].item()
    sma = data['Close'].rolling(window=window).mean().iloc[-1].item()
    return spot, sma
