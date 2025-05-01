import requests
import pandas as pd
from datetime import datetime, timedelta

def get_usd_exchange_rate(target_currency: str):
    url = f'https://open.er-api.com/v6/latest/USD'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['rates'].get(target_currency)
    else:
        print("Error fetching data:", response.status_code)
        return None

def generate_fake_historical_data(currency_code: str, days: int = 10):
    """
    Since the free API does not support historical data, we'll simulate the last 10 days
    by applying small random variations around today’s rate.
    """
    import random
    today_rate = get_usd_exchange_rate(currency_code)
    if today_rate is None:
        return pd.DataFrame()

    dates = [datetime.now() - timedelta(days=i) for i in range(days)]
    dates.reverse()  # Oldest first

    rates = [round(today_rate + random.uniform(-0.02, 0.02) * today_rate, 4) for _ in dates]

    return pd.DataFrame({
        'Date': [d.strftime('%Y-%m-%d') for d in dates],
        f'USD to {currency_code}': rates
    })

# Generate data for both currencies
df_cop = generate_fake_historical_data('COP')
df_eur = generate_fake_historical_data('EUR')

# Merge both into one DataFrame
df_merged = pd.merge(df_cop, df_eur, on='Date')
print(df_merged)

    
    