import os
import time
import datetime

import requests
import pandas as pd

# -------- Tiingo API를 사용하여 주식 데이터를 수집하는 스크립트 --------
# 작성자 : 김태형
# 이 스크립트는 Tiingo API를 통해 주식 데이터를 수집하고 CSV 파일로 저장합니다.

# 기본 수집 정보 설정 (토큰, 시작일, 종료일)
TIINGO_TOKEN = os.getenv('TIINGO_TOKEN')
START_DATE = '1980-01-01'
END_DATE = '2025-05-11'

# Tiingo API를 사용하여 특정 티커의 데이터를 가져오는 함수
# 작성자 : 김태형
def get_ticker_data(ticker):
    url = f'https://api.tiingo.com/tiingo/daily/{ticker}/prices?token=\
{TIINGO_TOKEN}&startDate={START_DATE}&endDate={END_DATE}&format=csv'
    print(f"Requesting {url}")
    headers = {
        'Content-Type': 'application/json',
    }
    # 요청 보내서 데이터 가져오기
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
        with open(f'./stock/{ticker}.csv', 'wb') as f:
            f.write(r.content)
        print(f"✅ {ticker} data downloaded successfully.")
    else:
        print(f"❌ Error: {r.status_code} - {r.text}")
        return False
    return False

# CSV 파일에서 ETF, Stock 티커 목록을 읽어오는 함수
# 작성자 : 김태형
def open_csv_get_ticker():
    df_stock = pd.read_csv('./ticker_stock.csv', encoding='utf-8')
    df_stock = df_stock.rename(columns={'Symbol': 'SYMBOL', 
                                        'Name': 'NAME', 
                                        'Last Sale': 'LAST PRICE', 
                                        '% Change': '% CHANGE', 
                                        'Sector' : 'SECTOR'})
    df_etf = pd.read_csv('./ticker_etf.csv', encoding='utf-8')
    common_cols = df_etf.columns.intersection(df_stock.columns)
    df = pd.concat([df_stock[common_cols], 
                    df_etf[common_cols]], 
                    ignore_index=True).dropna()
    return (df['SYMBOL'][:-1])

# 메인 함수
# 작성자 : 김태형
if __name__ == "__main__":
    df = open_csv_get_ticker()
    last_crolling = 0

    # 이전 crolling 상태를 확인하기 위한 파일 읽기
    try:
        with open('./idx.lc', 'r') as f:
            lines = f.readlines()
            last_crolling = int(lines[-1].split(' ')[-1]) if lines else 0
    except FileNotFoundError:
        print("No previous crolling file found. Starting from the beginning.")

    # 모든 데이터 티커에 대해 crolling 수행
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