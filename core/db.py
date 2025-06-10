import os
import pickle

import pandas as pd
from scipy.spatial import ConvexHull
import numpy as np
from pathlib import Path
import sqlite3
import json


from clustering.kmeans_module import *
from clustering.sector_visualization import sector_visualization


# ------- DB 초기화 및 데이터 로딩 ------
# 작성자 : 김태형
DB_PATH = "./core/strategy.db"
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS max_strategy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_return REAL NOT NULL,
                strategy TEXT NOT NULL
            );
        """)
        conn.commit()

# DB 초기화
init_db()

if not os.path.exists('./data/ticker_etf.csv') or \
    not os.path.exists('./data/ticker_stock.csv'):
    raise FileNotFoundError("필요한 CSV 파일이 존재하지 않습니다. \
                            ./data/ 폴더에 ticker_etf.csv와 \
                            ticker_stock.csv 파일이 있어야 합니다.")
print("DB Initialize...")

# ETF 티커 데이터 로딩 및 전처리
df_etf = pd.read_csv('./data/ticker_etf.csv', encoding='utf-8')
df_etf = df_etf.iloc[:-1]
df_etf = df_etf.drop("1 yr % CHANGE", axis=1)
df_etf['SECTOR'] = "ETF"

# 주식 티커 데이터 로딩 및 전처리
df_stock = pd.read_csv('./data/ticker_stock.csv', encoding='utf-8')
df_stock = df_stock.rename(columns={'Symbol': 'SYMBOL', 
                                    'Name': 'NAME',
                                    'Last Sale': 'LAST PRICE', 
                                    '% Change': '% CHANGE',
                                    'Sector' : 'SECTOR'})
df_stock['SECTOR'] = df_stock['SECTOR'].fillna('N/A')

# 공통 컬럼 추출 및 데이터 병합 (주식 & ETF)
common_cols = df_etf.columns.intersection(df_stock.columns)
df = pd.concat([df_stock[common_cols],
                df_etf[common_cols]], 
                ignore_index=True).dropna()
print("DB Create Complete...")


# ------- feature 추출 및 데이터 정상치/이상치 분리 -------
# 작성자 : 김동혁

# 재시작 할 때마다 새로 feature 추출 및 정상치/이상치 분류를 하지 않도록 캐시 경로 설정
FEATURE_CACHE_PATH = Path("models/pretrained_feature.pkl")
NORMAL_OUTLIER_CACHE_PATH = Path("models/pretrained_normal_outlier.pkl")

# make_feature를 사용하여 사전에 feature 추출
# find_outlier를 사용하여 사전에 정상치/이상치 데이터 분리
# 작성자 : 김동혁
def get_feature_data_db(df_symbols=None,
                            *,
                            force_refresh=False,
                            feature_cache_path=FEATURE_CACHE_PATH,
                            normal_outlier_cache_path=NORMAL_OUTLIER_CACHE_PATH):
    if df_symbols is None:
        df_symbols = df['SYMBOL'][:-1].tolist()
    
    if feature_cache_path.exists() and normal_outlier_cache_path.exists()\
        and not force_refresh:
        with feature_cache_path.open("rb") as f1,\
            normal_outlier_cache_path.open("rb") as f2:
            print(f"📄 캐시 로드: {feature_cache_path}, {normal_outlier_cache_path}")
            return pickle.load(f1), pickle.load(f2)

    # if normal_outlier_cache_path.exists() and not force_refresh:
    #     with normal_outlier_cache_path.open("rb") as f2:
    #         print(f"📄 캐시 로드: {normal_outlier_cache_path}")
    #         return pickle.load(f2)
        
    print("🧮 feature 및 normal, outlier 재계산 중 …")
    # 1. 전체 데이터 로딩 및 전처리
    df_list = read_csv_files_year_filter(df_symbols)
    if df_list is None:
        raise ValueError("read_csv_files_year_filter 함수가 None을 반환했습니다. 데이터 확인이 필요합니다.")
    
    start_date, end_date = find_shortest_period(df_list)
    if (start_date is None) or (end_date is None):
        raise ValueError("find_shortest_period 함수가 None을 반환했습니다. 데이터 확인이 필요합니다.")
    
    filtered_df_list = removed_stocks(df_list, end_date)
    if filtered_df_list is None:
        raise ValueError("removed_stocks 함수가 None을 반환했습니다. 데이터 확인이 필요합니다.")
    
    trimmed_list = same_period(filtered_df_list, start_date, end_date)
    if trimmed_list is None:
        raise ValueError("same_period 함수가 None을 반환했습니다. 데이터 확인이 필요합니다.")
    
    # 2. 특성 추출
    pretrained_feature_data = make_feature_df(trimmed_list)
    if pretrained_feature_data is None:
        raise ValueError("make_feature_df 함수가 None을 반환했습니다. 데이터 확인이 필요합니다.")

    feature_cache_path.parent.mkdir(parents=True, exist_ok=True)
    with feature_cache_path.open("wb") as f:
        pickle.dump(pretrained_feature_data, f)
        print(f"💾feature 캐시 저장 완료: {feature_cache_path}")

    # 3. 이상치 처리
    pretrained_normal_data, pretrained_outlier_data = find_outlier(pretrained_feature_data)
    if (pretrained_normal_data is None) or (pretrained_outlier_data is None):
        raise ValueError("find_outlier 함수가 None을 반환했습니다. 데이터 확인이 필요합니다.")

    normal_outlier_cache_path.parent.mkdir(parents=True, exist_ok=True)
    with normal_outlier_cache_path.open("wb") as f:
        pickle.dump((pretrained_normal_data, pretrained_outlier_data), f)
        print(f"💾정상치/이상치 캐시 저장 완료: {normal_outlier_cache_path}")

    return pretrained_feature_data, pretrained_normal_data, pretrained_outlier_data


# ------- 모든 주가 데이터 사전 트레이닝 -------
# 작성자 : 김태형

# 재시작 시마다 k_means를 새로 계산하지 않도록 캐시 경로 설정
CACHE_PATH = Path("models/pretrained_data.pkl")


# k_means를 사용하여 사전 트레이닝 데이터 생성 함수
# 이 함수는 캐시를 사용하여 성능을 최적화합니다.
# 작성자 : 김태형
def get_pretrained_data_db(df_symbols=None,
                            *,
                            force_refresh=False,
                            cache_path=CACHE_PATH,
                            sector_cache_path=Path("models/pretrained_sectors.pkl")):
    if df_symbols is None:
        df_symbols = df['SYMBOL'][:-1].tolist()

    if cache_path.exists() and sector_cache_path.exists() and not force_refresh:
        with cache_path.open("rb") as f1, sector_cache_path.open("rb") as f2:
            print(f"📄 캐시 로드: {cache_path}, {sector_cache_path}")
            return pickle.load(f1), pickle.load(f2)

    print("🧮 k_means 재계산 중 …")
    pretrained_data = k_means(df_symbols)
    if pretrained_data is None:
        raise ValueError("k_means 함수가 None을 반환했습니다. 데이터 확인이 필요합니다.")

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open("wb") as f:
        pickle.dump(pretrained_data, f)
        print(f"💾 캐시 저장 완료: {cache_path}")

    pretrained_sectors = sector_visualization()
    if pretrained_sectors is None:
        raise ValueError("sector_visualization 함수가 None을 반환했습니다. 데이터 확인이 필요합니다.")

    sector_cache_path.parent.mkdir(parents=True, exist_ok=True)
    with sector_cache_path.open("wb") as f:
        pickle.dump(pretrained_sectors, f)
        print(f"💾 섹터 캐시 저장 완료: {sector_cache_path}")

    return pretrained_data, pretrained_sectors

# 사전 트레이닝 데이터 로딩
print("Pretraining...")
pretrained_feature_data, pretrained_normal_data, pretrained_outlier_data = \
    get_feature_data_db()
pretrained_data, pretrained_sectors = get_pretrained_data_db()
cluster_map = pretrained_data.set_index("ticker")["cluster"].to_dict()

# 기본 클러스터 시각화를 위한 Convex Hull 생성
# Convex Hull을 사용하여 클러스터링 시각화
# 작성자 : 김태형
hull_list = []
for cluster in pretrained_data["cluster"].unique().tolist():
    cluster_points = pretrained_data[pretrained_data["cluster"] == cluster]
    if len(cluster_points) < 3:
        continue
    points = cluster_points[["PC1", "PC2"]].values
    hull = ConvexHull(points)
    ordered = np.append(hull.vertices, hull.vertices[0])
    hull_coords = [{"x": float(points[i][0]),
                    "y": float(points[i][1])} for i in ordered]
    hull_list.append({
        "cluster": int(cluster),
        "hull_coords" : hull_coords,
        })

max_strategy = list()


# ------- DB 접근 Getter ------
# 모든 티커 정보 및 클러스터 정보를 반환하는 함수
# 작성자 : 김태형
def get_all_tickers():
    global df
    return {
        row["SYMBOL"]: {
            **row,
            "CLUSTER": cluster_map.get(row["SYMBOL"], None)
        }
        for row in df.to_dict(orient="records")
    }

# 모든 클러스터의 Convex Hull 좌표를 반환하는 함수
# 작성자 : 김태형
def get_hull_list():
    global hull_list
    return hull_list

# 데이터의 feature를 추출하는 함수
# 작성자 : 김동혁
def get_pretrained_feature():
    global pretrained_feature_data
    return pretrained_feature_data

# 수집한 데이터의 정상치/이상치 데이터를 분류하는 함수
# 작성자 : 김동혁
def get_pretrained_normal_outlier():
    global pretrained_normal_data, pretrained_outlier_data
    return pretrained_normal_data, pretrained_outlier_data

# 사전 트레이닝 데이터를 반환하는 함수
# 작성자 : 김태형
def get_pretrained_data():
    global pretrained_data
    return pretrained_data

# 심볼을 통해서 티커 정보를 반환하는 함수
# 작성자 : 김태형
def get_tickers_by_symbol(symbols):
    global df
    if isinstance(symbols, str):
        symbols = [symbols]
    return {
        row["SYMBOL"]: {
            **row,
            "CLUSTER": cluster_map.get(row["SYMBOL"], None)
        }
        for row in df[df["SYMBOL"].isin(symbols)].to_dict(orient="records")
    }

# 섹터 시각화 결과를 반환하는 함수
# 작성자 : 김태형
def get_pretrained_sectors():
    global pretrained_sectors
    return pretrained_sectors

def get_max_strategy():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            SELECT total_return, strategy
            FROM max_strategy
            ORDER BY total_return DESC
            LIMIT 5
        """)
        rows = cursor.fetchall()
        return [
            {
                "total_return": r[0],
                "strategy": json.loads(r[1])  # JSON 문자열 → dict
            }
            for r in rows
        ]

def update_max_strategy(max_total_return, strategy):
    strategy_json = json.dumps(strategy, sort_keys=True)  # dict → JSON 문자열

    with sqlite3.connect(DB_PATH) as conn:
        # 현재 개수 확인
        cursor = conn.execute("SELECT COUNT(*) FROM max_strategy")
        count = cursor.fetchone()[0]

        if count < 5:
            conn.execute("INSERT INTO max_strategy (total_return, strategy) VALUES (?, ?)",
                         (max_total_return, strategy_json))
            conn.commit()
            return

        # 최소 수익률 가져오기
        cursor = conn.execute("""
            SELECT id, total_return
            FROM max_strategy
            ORDER BY total_return ASC
            LIMIT 1
        """)
        min_id, min_return = cursor.fetchone()

        if max_total_return > min_return:
            conn.execute("DELETE FROM max_strategy WHERE id = ?", (min_id,))
            conn.execute("INSERT INTO max_strategy (total_return, strategy) VALUES (?, ?)",
                         (max_total_return, strategy_json))
            conn.commit()
