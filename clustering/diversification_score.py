import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import pdist

import core.db

# 클러스터 분포 기반 점수화
# 작성자 : 김동혁
def diversification_score_cluster(df, selected_tickers, weights, n_clusters=4):
    '''
    선택된 종목들이 클러스터에 얼마나 고르게 분포되어 있는지 평가
    여러 클러스터에 고르게 분포될수록 분산 투자가 잘 된 것으로 간주
    종목별 비중 가중치 부여
    '''
    selected = df[df['ticker'].isin(selected_tickers)].copy()
    # 종목별 투자 비중(가중치) 할당
    selected['weight'] = [weights[t] for t in selected['ticker']]

    # 클러스터별 투자 비중의 합(선택되지 않은 클러스터는 0으로 채워짐)
    cluster_weights = selected.groupby('cluster')['weight']\
        .sum().reindex(range(n_clusters), fill_value=0)
    
    # 균등성 점수 (정규화 전): 각 클러스터별 비중의 제곱합을 1에서 뺀 값
    raw_score = 1 - np.sum(cluster_weights ** 2)
    # 이론적 최대 점수 (모든 클러스터에 균등 분포 시)
    max_score = 1 - 1 / n_clusters if n_clusters > 1 else 0
    # 최종 점수(0~1): 실제 점수를 최대 점수로 나눠 정규화
    score = raw_score / max_score if max_score > 0 else 0
    
    return score

# 정상치 데이터의 클러스터별 feature 평균으로 이상치 데이터 대체
# 작성자 : 김동혁
def replace_normal_avg(df):
    normal_df, outlier_df = core.db.get_pretrained_normal_outlier()

    # 클러스터 정보 병합
    cluster_info = df[['ticker', 'cluster']]
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
    avg_normal_df_cluster = normal_df_cluster\
        .groupby('cluster')[numeric_cols].mean().reset_index()
    
    # 이상치 데이터의 feature를 정상치 데이터 feature의 평균으로 대체
    for col in numeric_cols:
        outlier_df_cluster[col] = outlier_df_cluster['cluster'].map(
            avg_normal_df_cluster[col]
        )
    
    df = pd.concat([normal_df_cluster, outlier_df_cluster], axis=0)
    return df

# 종목별 분산도 계산
# 작성자 : 김동혁
def diversification_score_ndim(df, selected_tickers, weights):
    '''
    n차원 지표 공간에서 선택 종목들이 얼마나 퍼져 있는지
    각 종목쌍의 유클리드 거리 * 두 종목의 가중치 곱의 가중평균을 산출
    최종적으로 전체 종목 중 최대 거리로 정규화
    '''
    avg_df = replace_normal_avg(df)
    
    numeric_cols = avg_df.drop(
        columns=['ticker', 'cluster']
    ).columns.tolist()
    selected = avg_df[avg_df['ticker'].isin(selected_tickers)].copy()
    # 종목별 투자 비중
    selected['weight'] = [weights[t] for t in selected['ticker']]
    # n차원 지표값 numpy 배열로 추출
    coords = selected[numeric_cols].values
    w = selected['weight'].values
    n = len(coords)

    weighted_sum = 0.0    # 거리 * 가중치곱의 총합
    weight_total = 0.0    # 모든 종목쌍의 가중치곱 총합
    for i in range(n):
        for j in range(i+1, n):
            # 두 종목의 n차원 유클리드 거리
            dist = np.linalg.norm(coords[i] - coords[j])
            pair_weight = w[i] * w[j]
            weighted_sum += dist * pair_weight
            weight_total += pair_weight

    # 비정상적인 경우 처리
    if weight_total == 0:
        return 0.0
    
    # 가중평균 거리(비중이 높은 종목쌍의 거리가 멀수록 점수 높아짐)
    weighted_mean_dist = weighted_sum / weight_total
    # 전체 종목 중 최대 거리로 정규화
    all_coords = avg_df[numeric_cols].values
    # 전체 종목쌍 중 가장 먼 거리
    max_dist = pdist(all_coords).max()
    # 전체 중 최대 거리로 나누어 0~1 사이 정규화된 점수
    score = weighted_mean_dist / max_dist
    return score

# 혼합 점수(클러스터+좌표)
# 작성자 : 김동혁
def diversification_score_mixed(
        df, selected_tickers, weights, n_clusters=4, alpha=0.5
):
    if len(selected_tickers) < 2:
        print("최소 2개 이상의 종목을 담아야 분산 투자 점수가 산정됩니다.")
        return None
    score_cluster = diversification_score_cluster(
        df, selected_tickers, weights, n_clusters
    )
    score_pca = diversification_score_ndim(df, selected_tickers, weights)
    final_score = alpha * score_cluster + (1 - alpha) * score_pca
    return final_score


if __name__ == "__main__":
    result_df = core.db.get_pretrained_data()

    # 임의로 종목 선택(사용자 선택 종목)
    selected_tickers = ['AAON', 'ZEOWW', 'AAA', 'ZURA']
    # 임의로 투자 비중 설정(사용자 종목별 지정 투자 비율)
    weights = {'AAON':0.2, 'ZEOWW':0.4, 'AAA':0.2, 'ZURA':0.2}

    score = diversification_score_mixed(
        result_df, selected_tickers, weights, n_clusters=4, alpha=0.5
    )
    print("분산 투자 점수:", score)