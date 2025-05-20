import pandas as pd
from clustering.Kmeans import *
import os
from scipy.spatial import ConvexHull
import numpy as np
import pickle
from pathlib import Path

print("Loading data...")
df_etf = pd.read_csv('./collect/ticker_etf.csv', encoding='utf-8')
df_etf = df_etf.iloc[:-1]
df_etf = df_etf.drop("1 yr % CHANGE", axis=1)
df_etf['SECTOR'] = "ETF"

df_stock = pd.read_csv('./collect/ticker_stock.csv', encoding='utf-8')

df_stock = df_stock.rename(columns={'Symbol': 'SYMBOL', 'Name': 'NAME', 'Last Sale': 'LAST PRICE', '% Change': '% CHANGE', 'Sector' : 'SECTOR'})

common_cols = df_etf.columns.intersection(df_stock.columns)

df_stock['SECTOR'] = df_stock['SECTOR'].fillna('N/A')
df = pd.concat([df_stock[common_cols], df_etf[common_cols]], ignore_index=True).dropna()

print("DB Create Complete...")

def get_all_tickers():
    global df
    return {
        row["SYMBOL"]: {
            **row,
            "CLUSTER": cluster_map.get(row["SYMBOL"], None)  # SYMBOL → ticker 매핑
        }
        for row in df.to_dict(orient="records")
    }

def get_hull_list():
    global hull_list
    return hull_list

CACHE_PATH = Path("models/pretrained_data.pkl")   # 원하는 위치·이름으로 변경

def get_pretrained_data_db(df_symbols=df['SYMBOL'][:-1].tolist(), *, force_refresh=False, cache_path=CACHE_PATH):
    """
    df_symbols : 시계열 등 전처리 끝난 DataFrame의 SYMBOL 컬럼 (iterable)
    force_refresh: True면 캐시 무시하고 새로 계산
    cache_path   : 캐시 파일 경로
    """
    # 1) 캐시가 있고 강제 새로고침이 아니면 → 바로 로드
    if cache_path.exists() and not force_refresh:
        with cache_path.open("rb") as f:
            print(f"📄 캐시 로드: {cache_path}")
            return pickle.load(f)

    # 2) 없으면 k_means 재계산
    print("🧮 k_means 재계산 중 …")
    pretrained_data = k_means(df_symbols)

    # 3) 캐시 저장
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open("wb") as f:
        pickle.dump(pretrained_data, f)
        print(f"💾 캐시 저장 완료: {cache_path}")

    return pretrained_data

def get_pretrained_data():
    global pretrained_data
    return pretrained_data


pretrained_data = get_pretrained_data_db()

print("Pretraining...")
cluster_map = pretrained_data.set_index("ticker")["cluster"].to_dict()

# PreTrain Convex Hull
hull_list = []
for cluster in pretrained_data["cluster"].unique().tolist():
    # Convex Hull을 사용하여 클러스터링
    cluster_points = pretrained_data[pretrained_data["cluster"] == cluster]
    if len(cluster_points) < 3:
        continue
    points = cluster_points[["PC1", "PC2"]].values
    hull = ConvexHull(points)
    ordered = np.append(hull.vertices, hull.vertices[0])
    hull_coords = [{"x": float(points[i][0]), "y": float(points[i][1])} for i in ordered]
    hull_list.append({
        "cluster": int(cluster),
        "hull_coords" : hull_coords,
        })