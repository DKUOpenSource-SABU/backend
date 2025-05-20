import os
import time
import datetime

import requests
import pandas as pd

TIINGO_TOKEN = os.getenv('TIINGO_TOKEN')
START_DATE = '1980-01-01'  # 가능한 가장 이른 날짜
END_DATE = '2025-05-11'

def get_ticker_data(ticker):

    url = f'https://api.tiingo.com/tiingo/daily/{ticker}/prices?token=\
{TIINGO_TOKEN}&startDate={START_DATE}&endDate={END_DATE}&format=csv'
    print(f"Requesting {url}")
    headers = {
        'Content-Type': 'application/json',
    }

    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        if ':' in str(r.content).strip():
            if '^' in str(r.content).strip():
                return False
            print(f"❌ Error: {r.status_code} - {r.text}")
            user_input = int(input("Input 1 Retry..."))
            if user_input == 1:
                print("Retrying...")
                time.sleep(5)
                return True
            else:
                print("Next...")
                return False
            return False
        with open(f'./stock/{ticker}.csv', 'wb') as f:
            f.write(r.content)
        print(f"✅ {ticker} data downloaded successfully.")
    else:
        print(f"❌ Error: {r.status_code} - {r.text}")
        return False
    return False

def open_csv_get_ticker():
    df_stock = pd.read_csv('./ticker_stock.csv', encoding='utf-8')
    df_stock = df_stock.rename(columns={'Symbol': 'SYMBOL', 'Name': 'NAME', 'Last Sale': 'LAST PRICE', '% Change': '% CHANGE', 'Sector' : 'SECTOR'})
    df_etf = pd.read_csv('./ticker_etf.csv', encoding='utf-8')
    common_cols = df_etf.columns.intersection(df_stock.columns)
    df = pd.concat([df_stock[common_cols], df_etf[common_cols]], ignore_index=True).dropna()
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