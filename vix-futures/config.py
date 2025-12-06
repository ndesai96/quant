TABLE_NAME = 'futures'
REGION = 'us-east-1'
CBOE_URL = "https://www.cboe.com/us/futures/market_statistics/settlement/csv?dt={date}"
VIX_CENTRAL_URL = "http://vixcentral.com/"
FUTURES_MONTH_CODES = {
    'Jan': 'F', 'Feb': 'G', 'Mar': 'H', 'Apr': 'J', 'May': 'K', 'Jun': 'M',
    'Jul': 'N', 'Aug': 'Q', 'Sep': 'U', 'Oct': 'V', 'Nov': 'X', 'Dec': 'Z'
}