import pandas as pd
from pathlib import Path

DATA_PATH = Path("__file__").resolve().parent.parent / "stock"

def load_data(tickers: list, start_date: str, end_date: str) -> dict:
    data = {}
    for ticker in tickers:
        file_path = DATA_PATH / f"{ticker}.csv"
        if not file_path.exists():
            raise FileNotFoundError(f"File {file_path} does not exist")

        df = pd.read_csv(file_path)

        if "date" not in df.columns:
            raise ValueError(f"{ticker} CSV must have a 'date' column")

        df.columns = df.columns.str.capitalize()
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.set_index("Date")
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        df = df.loc[(start <= df.index) & (df.index <= end)]

        if df.empty:
            raise ValueError(f"{ticker} does not have data about requested dates({start_date}~{end_date})")

        required_cols = {"Open", "High", "Low", "Close", "Volume"}
        if not required_cols.issubset(df.columns):
            raise ValueError(f"{ticker} is missing required columns.")

        data[ticker] = df

        print(f"✅ {ticker}:")
        print(df.head())
        print(df.tail())

    return data
