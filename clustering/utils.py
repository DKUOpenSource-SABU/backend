
import os

import pandas as pd
import glob

def read_csv_files():
    base_path = '../collect/stock/'
    all_files = glob.glob(os.path.join(base_path, "*.csv"))

    df_list = []

    for file_path in all_files:
        ticker = os.path.splitext(os.path.basename(file_path))[0]
        df = pd.read_csv(file_path, parse_dates=['date'])
        df['ticker'] = ticker  # 티커 컬럼 추가
        df_list.append(df)

    df_all = pd.concat(df_list, ignore_index=True)
    return df_all

if __name__ == "__main__":
    read_csv_files()