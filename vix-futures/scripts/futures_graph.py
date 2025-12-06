import matplotlib.pyplot as plt
import pandas as pd
import json
from datetime import datetime, timedelta
from futures import get_historical_futures_data, get_realtime_futures_data
from vix import get_vix_data

# Run with:
# poetry run python -m scripts.futures_graph

def plot(data: dict):
    symbols = {item['symbol'] for item in data['realtime']}

    plt.figure(figsize=(12, 7))

    plt.axhline(y=data['spot'],
                linestyle='--',
                alpha=0.7,
                label='Spot',
                color='red')

    historical_data = data['historical']
    sorted_dates = sorted(historical_data.keys())

    count = 0
    for date in sorted_dates:
        count += 1
        if count % 7 != 0:
            continue
        records = historical_data[date]
        # Filter records to only include symbols found in realtime data
        filtered_records = [r for r in records if r['symbol'] in symbols]
        
        if filtered_records:
            df = pd.DataFrame(filtered_records)
            df['expiration_date'] = pd.to_datetime(df['expiration_date'])
            df = df.sort_values('expiration_date')
            
            plt.plot(df['expiration_date'], df['price'], 
                     marker='o', 
                     linestyle='--', 
                     alpha=0.7, 
                     label=f'Historical {date}')

    df_realtime = pd.DataFrame(data['realtime'])
    df_realtime['expiration_date'] = pd.to_datetime(df_realtime['expiration_date'])
    df_realtime = df_realtime.sort_values('expiration_date')

    plt.plot(df_realtime['expiration_date'], df_realtime['price'], 
             marker='o', 
             linewidth=2.5, 
             color='black', 
             label='Realtime')

    plt.title('Futures Price Term Structure')
    plt.xlabel('Expiration Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    today = datetime.now()
    start_date = today - timedelta(days=60)
    end_date = today

    data = {
        'historical': get_historical_futures_data(start_date, end_date),
        'realtime': get_realtime_futures_data(),
        'spot': get_vix_data()['spot']
    }
    plot(data)