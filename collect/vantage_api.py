import os

import requests
import pandas as pd

API_IDX = 1
API_KEY = os.getenv(f'ALPHA_VANTAGE_API_KEY{API_IDX}')

def get_ticker_data(ticker):
    global API_KEY
    global API_IDX
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&\
            symbol={ticker}&interval=5min&apikey={API_KEY}&outputsize=full\
            &datatype=csv'
    r = requests.get(url)
    if r.status_code == 200:
        if ':' in str(r.content).strip():
            print(f"Try with {API_KEY}")
            API_IDX += 1
            if API_IDX > 8:
                print(f"❌ Error: API limit reached. Please try again later.")
                exit(1)
            API_KEY = os.getenv(f'ALPHA_VANTAGE_API_KEY{API_IDX}')
            return True
        with open(f'./stock/{ticker}.csv', 'wb') as f:
            f.write(r.content)
        print(f"✅ {ticker} data downloaded successfully.")
    else:
        print(f"❌ Error: {r.status_code} - {r.text}")
    return False

def open_csv_get_ticker():
    df = pd.read_csv('./ticker.csv', encoding='utf-8')
    return (df['SYMBOL'][:-1])

df = open_csv_get_ticker()

last_crolling = 0

try:
    with open('./idx.lc', 'r') as f:
        lines = f.readlines()
        last_crolling = int(lines[-1].split(' ')[-1]) if lines else 0
except FileNotFoundError:
    print("No previous crolling file found. Starting from the beginning.")

for idx, ticker in enumerate(df):
    if idx <= last_crolling:
        continue
    if os.path.exists(f'./stock/{ticker}.csv'):
        print(f"✅ {ticker} already exists.")
        continue
    print(f"Processing {idx} - {ticker}")
    while get_ticker_data(ticker):
        pass
    with open(f'./idx.lc', 'w') as f:
        f.write(f'Last Crolling {idx}\n')