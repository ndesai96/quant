import json
import yfinance as yf

def lambda_handler(event, context):
    vix_spot, vix_sma = get_history('^VIX', 20)

    signal = "STABLE"
    if vix_spot > (vix_sma * 1.10):
        signal = "SPIKING"
    elif vix_spot < (vix_sma * 0.90):
        signal = "CRUSHED"
    
    vix_3m_spot = get_spot('^VIX3M')
    contango_spread = (vix_3m_spot - vix_spot) / vix_spot

    if contango_spread >= 0.15:
        contango_signal = "YELLOW (Contango - Extreme Complacency)"
    elif contango_spread >= 0:
        contango_signal ="GREEN (Contango - Normal Market)"
    elif contango_spread > -0.05:
        contango_signal = "ORANGE (Backwardation - Market Stress)"
    else:
        contango_signal = "RED (Deep Backwardation - Severe Stress/Panic)"

    response_data = {
        'vix': {
            'spot': vix_spot,
            'sma': vix_sma,
            'diff_pct': '{:.2f}%'.format(((vix_spot - vix_sma) / vix_sma) * 100),
            'signal': signal,
            'vix_3m_spot': vix_3m_spot,
            'contango_spread': '{:.2f}%'.format(contango_spread * 100),
            'contango_signal': contango_signal
        }
    }

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(response_data)
    }


def get_history(ticker, window=20) -> tuple[float, float]:
    data = yf.download(ticker, period="6mo", interval="1d", progress=False, auto_adjust=True)
    spot = data['Close'].ffill().iloc[-1].item()
    sma = data['Close'].rolling(window=window).mean().iloc[-1].item()
    return spot, sma

def get_spot(ticker) -> float:
    data = yf.download(ticker, period="5d", interval="1d", progress=False, auto_adjust=True)
