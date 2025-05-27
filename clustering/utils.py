
import os

import pandas as pd
import glob
from tqdm import tqdm

# -------- CSV 파일을 읽어와서 데이터프레임으로 반환하는 스크립트 --------
# 작성자 : 김태형
# 이 스크립트는 ./collect/stock/ 폴더에 있는 모든 CSV 파일을 읽어 df로 변환
# tqdm을 사용하여 진행 상황을 표시합니다.
def read_csv_files():
    base_path = './collect/stock/'
    all_files = glob.glob(os.path.join(base_path, "*.csv"))

    df_list = []
    try:
        for file_path in tqdm(all_files, desc="Loading CSV files"):
            ticker = os.path.splitext(os.path.basename(file_path))[0]
            df = pd.read_csv(file_path, parse_dates=['date'])
            df['ticker'] = ticker  # 티커 컬럼 추가
            df_list.append(df)

    except ValueError as e:
        print(f"❌ Error: {e}")
        print(f"❌ Error: {file_path} - {e}", flush=True)
    df_list = [df for df in df_list if not df.empty]
    df_all = pd.concat(df_list, ignore_index=True)
    return df_all

if __name__ == "__main__":
    read_csv_files()