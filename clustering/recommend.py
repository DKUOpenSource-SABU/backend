import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import euclidean_distances

import core.db



def recommend(tickers):
    normal_df, outlier_df = core.db.get_pretrained_normal_outlier()

    # 입력 ticker가 데이터에 없을 경우
    not_found = [t for t in tickers if t not in normal_df['ticker'].values]
    if not_found:
        raise ValueError(f"선택한 티커에 해당하는 데이터가 없습니다: {not_found}")
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(normal_df.drop(columns=['ticker']))

    # 선택 종목 추출 및 평균 feature 계산
    selected_ticker = tickers
    selected_rows = normal_df[normal_df['ticker'].isin(selected_ticker)]
    selected_scaled = scaler.transform(selected_rows.drop(columns=['ticker']))
    center_point = selected_scaled.mean(axis=0).reshape(1, -1)

    # 전체 종목과 중심점 간 거리 계산
    distances = euclidean_distances(center_point, X_scaled).flatten()

    # 선택 종목은 추천에서 제외
    selected_indices = normal_df.index[normal_df['ticker'].isin(selected_ticker)].tolist()
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
    recommended_stocks = normal_df.iloc[top5_indices_fixed]
    recommended_tickers = recommended_stocks['ticker'].tolist()

    return recommended_tickers


if __name__ == "__main__":
    # 사용자가 선택했다고 가정(예시 데이터)
    selected_ticker = ['AADR', 'CCM', 'AAL', 'ALLR', 'AA']
    # 추천 종목 출력
    recommend(selected_ticker)