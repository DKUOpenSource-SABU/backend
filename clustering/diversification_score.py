import numpy as np

import clustering.kmeans_module

# 클러스터 분포 기반 점수화
def diversification_score_cluster(df, selected_tickers, weights, n_clusters=4):
    '''
    선택된 종목들이 4개 클러스터에 얼마나 고르게 분포되어 있는지 평가
    여러 클러스터에 고르게 분포될수록 분산 투자가 잘 된 것으로 간주
    종목별 비중 가중치 부여
    '''
    if len(selected_tickers) < 4:
        print("최소 4개 이상의 종목을 담아야 분산 투자 점수가 산정됩니다.")
        return None
    # 선택 종목에 해당하는 클러스터 정보 추출
    selected = df[df['ticker'].isin(selected_tickers)].copy()
    selected['weight'] = [weights[t] for t in selected['ticker']]
    cluster_weights = selected.groupby('cluster')['weight'].sum().reindex(
        range(n_clusters), fill_value=0)
    score = 1 - np.sum(cluster_weights ** 2)
    return score


# 2차원 좌표 분포 기반 점수화
def diversification_score_pca(df, selected_tickers, weights):
    '''
    2차원 좌표상에서 선택 종목들이 얼마나 퍼져 있는지
    산포도 상의 분산 또는 평균 거리
    단순 평균이 아니라 가중 평균 거리(각 종목쌍의 거리 * 두 종목의 가중치 곱)
    '''
    if len(selected_tickers) < 4:
        print("최소 4개 이상의 종목을 담아야 분산 투자 점수가 산정됩니다.")
        return None
    # 선택 종목의 2차원 좌표 추출 및 가중치 부여
    selected = df[df['ticker'].isin(selected_tickers)].copy()
    selected['weight'] = [weights[t] for t in selected['ticker']]
    # 좌표 및 가중치 배열화
    coords = selected[['PC1', 'PC2']].values
    w = selected['weight'].values
    n = len(coords)

    # 모든 종목쌍 간 유클리드 거리 * 가중치 곱의 합 계산
    # 실제 투자 비중이 높을수록, 거리 효과가 더 크게 반영되도록 함
    weighted_sum = 0.0
    weight_total = 0.0
    for i in range(n):
        for j in range(i+1, n):
            dist = np.linalg.norm(coords[i] - coords[j])  # 두 종목의 좌표 거리
            pair_weight = w[i] * w[j]  # 두 종목의 가중치 곱
            weighted_sum += dist * pair_weight
            weight_total += pair_weight

    # 예외적 상황(가중치 곱의 총합이 0이 되는 경우)
    if weight_total == 0:
        return 0.0
    # 가중 평균 거리
    weighted_mean_dist = weighted_sum / weight_total

    # 정규화(전체 종목 중 최대 거리로 나눔)
    all_coords = df[['PC1', 'PC2']].values
    from scipy.spatial.distance import pdist
    max_dist = pdist(all_coords).max()
    score = weighted_mean_dist / max_dist
    return score


# 혼합 점수(클러스터+좌표)
def diversification_score_mixed(
        df, selected_tickers, weights, n_clusters=4, alpha=0.5):
    if len(selected_tickers) < 4:
        print("최소 4개 이상의 종목을 담아야 분산 투자 점수가 산정됩니다.")
        return None
    score_cluster = diversification_score_cluster(
        df, selected_tickers, weights, n_clusters)
    score_pca = diversification_score_pca(df, selected_tickers, weights)
    final_score = alpha * score_cluster + (1 - alpha) * score_pca
    return final_score


if __name__ == "__main__":
    result_df = clustering.kmeans_module.k_means()

    # 임의로 종목 선택(사용자 선택 종목)
    selected_tickers = ['AAON', 'ZEOWW', 'AAA', 'ZURA']

    # 임의로 투자 비중 설정(사용자 종목별 지정 투자 비율)
    weights = {'AAON':0.2, 'ZEOWW':0.4, 'AAA':0.2, 'ZURA':0.2}

    score = diversification_score_mixed(
        result_df, selected_tickers, weights, n_clusters=4, alpha=0.5)
    print("분산 투자 점수:", round(score, 3))