import os

import requests
import pandas as pd

# --------- Alpha Vantage API를 사용하여 주식 데이터를 수집하는 스크립트 --------
# 작성자 : 김태형
# Deprecated: 이 스크립트는 더 이상 사용되지 않습니다.
# Tiingo API를 사용하여 주식 데이터를 수집하는 것으로 대체되었습니다.
# 이 스크립트는 Alpha Vantage API를 통해 주식 데이터를 수집하고 CSV 파일로 저장합니다.
API_IDX = 1
API_KEY = os.getenv(f'ALPHA_VANTAGE_API_KEY{API_IDX}')

# Alpha Vantage API를 사용하여 특정 티커의 데이터를 가져오는 함수
# 작성자 : 김태형
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

# CSV 파일에서 ETF, Stock 티커 목록을 읽어오는 함수
# 작성자 : 김태형
def open_csv_get_ticker():
    df = pd.read_csv('./ticker.csv', encoding='utf-8')
    return (df['SYMBOL'][:-1])

# 주식 데이터를 수집하고 CSV 파일로 저장하는 메인 함수
# 작성자 : 김태형
if __name__ == "__main__":
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