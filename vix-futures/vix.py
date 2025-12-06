import yfinance as yf

def get_vix_data() -> dict:
    data = yf.download("^VIX", period="6mo", interval="1d", progress=False, auto_adjust=True)
    spot = data['Close'].ffill().iloc[-1].item()
    sma_10 = data['Close'].rolling(window=10).mean().iloc[-1].item()
    sma_20 = data['Close'].rolling(window=20).mean().iloc[-1].item()
    sma_50 = data['Close'].rolling(window=50).mean().iloc[-1].item()

    historical = {}

    for date, row in data.iterrows():
        historical[date.strftime('%Y-%m-%d')] = row['Close'].item()
    
    return {
        "spot": spot,
        "sma_10": sma_10,
        "sma_20": sma_20,
        "sma_50": sma_50,
        "diff_pct_10": '{:.2f}%'.format(((spot - sma_10) / sma_10) * 100),
        "diff_pct_20": '{:.2f}%'.format(((spot - sma_20) / sma_20) * 100),
        "diff_pct_50": '{:.2f}%'.format(((spot - sma_50) / sma_50) * 100),
        "historical": historical
    }   