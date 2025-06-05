import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import euclidean_distances
from collections import Counter

import core.db

# 정상치 데이터의 클러스터별 feature 평균으로 이상치 데이터 대체
# 작성자 : 김동혁
def outlier_replace_normal_avg():
    pretrained_df = core.db.get_pretrained_data()
    normal_df, outlier_df = core.db.get_pretrained_normal_outlier()
    
    # 클러스터 정보 병합
    cluster_info = pretrained_df[['ticker', 'cluster']]
    normal_df_cluster = pd.merge(
        normal_df, cluster_info, on='ticker', how='left'
    )
    outlier_df_cluster = pd.merge(
        outlier_df, cluster_info, on='ticker', how='left'
    )
    
    # feature 컬럼 추출 및 스케일링
    numeric_cols = normal_df_cluster.drop(
        columns=['ticker', 'cluster']
    ).columns.tolist()
    scaler = StandardScaler()
    scaled_values = scaler.fit_transform(normal_df[numeric_cols])
    for i, col in enumerate(numeric_cols):
        normal_df_cluster[col] = scaled_values[:, i]

    # 클러스터별 feature의 평균 계산
    avg_normal_df_cluster = normal_df_cluster.groupby('cluster')\
        [numeric_cols].mean().reset_index()
    
    # 이상치 데이터의 feature를 정상치 데이터 feature의 평균으로 대체
    for col in numeric_cols:
        outlier_df_cluster[col] = outlier_df_cluster['cluster'].map(
            avg_normal_df_cluster[col]
        )
    
    df = pd.concat([normal_df_cluster, outlier_df_cluster], axis=0)
    return df

# 거리 기반 종목 추천(상위 5개)
# 사용자가 선택한 종목의 클러스터 개수 정보 반영
# 작성자 : 김동혁
def recommend(tickers):
    df = outlier_replace_normal_avg()
    
    # 입력 ticker가 데이터에 없을 경우
    not_found = [t for t in tickers if t not in df['ticker'].values]
    if not_found:
        raise ValueError(f"선택한 티커에 해당하는 데이터가 없습니다: {not_found}")
    
    # feature 컬럼 추출
    numeric_cols = [
        col for col in df.columns if col not in ['ticker', 'cluster']
    ]
    # 전체 클러스터 목록
    all_clusters = sorted(df['cluster'].unique())
    
    # 선택 종목 정보
    selected_rows = df[df['ticker'].isin(tickers)]
    selected_clusters = selected_rows['cluster'].values

    # 클러스터별 선택 개수 집계 (선택되지 않은 클러스터는 0)
    cluster_count = Counter(selected_clusters)
    cluster_count_full = {c: cluster_count.get(c, 0) for c in all_clusters}

    # 선택 종목의 평균 feature (중심점)
    selected_scaled = selected_rows[numeric_cols].values
    center_point = selected_scaled.mean(axis=0).reshape(1, -1)

    clusters_sorted = sorted(cluster_count_full.items(), key=lambda x: x[1])
    recommended_tickers = []
    used_clusters = set()
    idx = 0
    
    # 추천 종목이 5개 미만이고, 아직 확인하지 않은 클러스터 우선순위가 남아 있을 때 반복
    while len(recommended_tickers) < 5 and idx < len(clusters_sorted):
        curr_min_count = clusters_sorted[idx][1]
        curr_clusters = [c for c, cnt in clusters_sorted 
                        if cnt == curr_min_count and c not in used_clusters]
        if not curr_clusters:
            idx += 1
            continue
        # 추천 후보 pool 생성
        candidate_df = df[
            (df['cluster'].isin(curr_clusters)) &
            (~df['ticker'].isin(tickers)) &    # 이미 선택한 종목 제회
            (~df['ticker'].isin(recommended_tickers))    # 이미 추천된 종목 제외
        ]
        if len(candidate_df) > 0:
            candidate_X = candidate_df[numeric_cols].values
            distances = euclidean_distances(center_point, candidate_X).flatten()
            sorted_idx = np.argsort(distances)[::-1]
            candidate_tickers = candidate_df.iloc[sorted_idx]['ticker'].tolist()
            for t in candidate_tickers:
                if len(recommended_tickers) < 5:
                    recommended_tickers.append(t)
                else:
                    break
        # 사용한 클러스터 기록 및 다음 우선순위로 이동
        used_clusters.update(curr_clusters)
        idx += 1

    return recommended_tickers


if __name__ == "__main__":
    # 사용자가 선택했다고 가정(예시 데이터)
    selected_ticker = ['TSLA', 'AAPL', 'AAL', 'ALLR', 'AA']
    # 추천 종목 출력
    recommend(selected_ticker)