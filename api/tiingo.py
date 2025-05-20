import os
import json
import requests
import pandas as pd

TIINGO_TOKEN = os.getenv('TIINGO_TOKEN')
CACHE_DIR = '.cache'
MEMORY_CACHE = {}

os.makedirs(CACHE_DIR, exist_ok=True)

# ---------- 공통 캐시 헬퍼 ----------

def get_cache_key(ticker, interval):
    return f"{ticker}_{interval}"

def get_cache_path(ticker, interval):
    return os.path.join(CACHE_DIR, f"{get_cache_key(ticker, interval)}.json")

def load_from_file_cache(ticker, interval):
    path = get_cache_path(ticker, interval)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None

def save_to_file_cache(ticker, interval, data):
    path = get_cache_path(ticker, interval)
    with open(path, 'w') as f:
        json.dump(data, f)

# ---------- 안전한 요청 ----------

def safe_tiingo_request(url: str):
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200 and res.text.strip():
            return res.json()
        else:
            print(f"[Tiingo] ⚠️ HTTP {res.status_code}: {res.text}")
            return None
    except requests.exceptions.JSONDecodeError as e:
        print(f"[Tiingo] ❌ JSONDecodeError: {e} | Raw: {res.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[Tiingo] ❌ Request failed: {e}")
        return None

# ---------- Public 인터페이스 ----------

def get_ticker_data(ticker):
    url = f'https://api.tiingo.com/tiingo/daily/{ticker}?token={TIINGO_TOKEN}'
    return safe_tiingo_request(url)

def get_ticker_news(ticker):
    url = f'https://api.tiingo.com/tiingo/news/?tickers={ticker}&token={TIINGO_TOKEN}&limit=10'
    return safe_tiingo_request(url)

STOCK_DIR = './collect/stock'


def load_stock_csv(ticker: str):
    path = os.path.join(STOCK_DIR, f"{ticker}.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"{ticker}.csv not found in ./stock")

    df = pd.read_csv(path, parse_dates=['date'])
    df = df.sort_values('date')  # 날짜 순 정렬
    return df


def df_to_dict(df: pd.DataFrame):
    return df.to_dict(orient='records')


def get_ticker_data_daily(ticker):
    df = load_stock_csv(ticker)[-60:]
    return df_to_dict(df)


def get_ticker_data_weekly(ticker):
    df = load_stock_csv(ticker)
    df.set_index('date', inplace=True)
    df_resampled = df.resample('W').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum',
    }).dropna().reset_index()[-60:]
    return df_to_dict(df_resampled)


def get_ticker_data_monthly(ticker):
    df = load_stock_csv(ticker)
    df.set_index('date', inplace=True)
    df_resampled = df.resample('ME').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna().reset_index()[-60:]
    return df_to_dict(df_resampled)


def get_ticker_data_annual(ticker):
    df = load_stock_csv(ticker)
    df.set_index('date', inplace=True)
    df_resampled = df.resample('YE').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna().reset_index()[-60:]
    return df_to_dict(df_resampled)
