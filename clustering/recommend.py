import numpy as np
from sklearn.metrics.pairwise import euclidean_distances

from kmeans_module import *



def make_df():
    df_list = read_csv_files_year_filter()
    start_date, end_date = find_shortest_period(df_list)
    filtered_df_list = removed_stocks(df_list, end_date)
    trimmed_list = same_period(filtered_df_list, start_date, end_date)
    features_df = make_feature_df(trimmed_list)
    df, outlier_df = find_outlier(features_df)

    return df 


def recommend(tickers):
    df = make_df()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df.drop(columns=['ticker']))

    # 선택 종목 추출 및 평균 feature 계산
    selected_ticker = tickers
    selected_rows = df[df['ticker'].isin(selected_ticker)]
    selected_scaled = scaler.transform(selected_rows.drop(columns=['ticker']))
    center_point = selected_scaled.mean(axis=0).reshape(1, -1)

    # 전체 종목과 중심점 간 거리 계산
    distances = euclidean_distances(center_point, X_scaled).flatten()

    # 선택 종목은 추천에서 제외
    selected_indices = df.index[df['ticker'].isin(selected_ticker)].tolist()
    distances[selected_indices] = -np.inf

    # 가장 먼 상위 5개 종목 추천
    valid_mask = distances != -np.inf
    valid_distances = distances[valid_mask]
    valid_indices = np.where(valid_mask)[0]
    # 상위 5개 종목 인덱스 추출
    top5_valid_indices = np.argpartition(valid_distances, -5)[-5:]
    top5_valid_indices = top5_valid_indices[np.argsort(
        valid_distances[top5_valid_indices])[::-1]]
    top5_indices_fixed = valid_indices[top5_valid_indices]

    # 인덱스에 해당하는 티커 추출
    recommended_stocks = df.iloc[top5_indices_fixed]
    recommended_tickers = recommended_stocks['ticker'].tolist()

    return recommended_tickers


# 사용자가 선택했다고 가정(예시 데이터)
selected_ticker = ['NUWE', 'CCM', 'DISTW', 'ALLR', 'QSIAW']

recommend(selected_ticker)