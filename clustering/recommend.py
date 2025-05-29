import numpy as np
from sklearn.metrics.pairwise import euclidean_distances

import clustering.kmeans_module
import core.db

def recommend(tickers):
    result_df = core.db.get_pretrained_data()
    pc_cols = ['PC1', 'PC2']

    # 선택한 종목의 행만 추출
    selected_rows = result_df[result_df['ticker'].isin(tickers)].dropna(subset=pc_cols)
    if selected_rows.empty:
        print("No selected rows found for the given tickers.")
        return None

    # 선택한 종목의 PC1, PC2를 이용하여 평균 지점 계산
    center_point = selected_rows[pc_cols].mean(axis=0) \
                                        .values.reshape(1, -1)

    # 전체 종목의 PC1, PC2 좌표
    all_points = result_df[pc_cols].values
    print("center_point.shape:", center_point)
    print("all_points.shape:", all_points.shape)

    # 중심점과 전체 종목 간 거리 계산
    distances = euclidean_distances(center_point, all_points).flatten()

    # 선택 종목의 인덱스
    selected_indices = result_df.index[result_df['ticker'].isin(tickers)].tolist()

    # 선택 종목은 추천 대상에서 제외
    distances[selected_indices] = -np.inf

    # 거리가 큰 순서대로 상위 5개 종목 인덱스 추출
    top5_indices = np.argpartition(distances, -5)[-5:]
    top5_indices = top5_indices[np.argsort(distances[top5_indices])[::-1]]

    return result_df.iloc[top5_indices]


if __name__ == "__main__":
    # 사용자가 선택했다고 가정(예시 데이터)
    selected_ticker = ['NUWE', 'CCM', 'DISTW', 'ALLR', 'QSIAW']
    # 추천 종목 출력
    recommend(selected_ticker)