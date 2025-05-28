import warnings

from clustering import utils
from sklearn.preprocessing import RobustScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import numpy as np

# 클러스터링 진행 중 발생하는 numpy 경고 무시
warnings.filterwarnings("ignore", category=RuntimeWarning)

# KMeans 클러스터링을 수행하는 함수
# 작성자 : 김태형
# 이 함수는 주어진 티커 목록에 대해 임시 KMeans 클러스터링을 수행
# 정확한 클러스터링과 무관하게 단순 클러스터링 결과를 반환합니다.
def k_means(tickers):
    df = utils.read_csv_files()
    df = df.fillna(df.mean(numeric_only=True))
    start_date = min(df[df['ticker'].isin(tickers)].date)
    end_date = max(df[df['ticker'].isin(tickers)].date)

    min_dates = df.groupby('ticker')['date'].min()
    latest_start = min_dates.max()
    #df = df[df['date'] >= latest_start]
    df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    features_by_ticker = (
    df.groupby('ticker')
    .agg({
        'close': ['mean', 'std'],
        'volume': 'mean',
        'divCash': 'sum',
        'splitFactor': 'sum'
    })
)
    features_by_ticker.columns = ['_'.join(col).strip() 
                                  for col in features_by_ticker.columns.values]
    features_by_ticker.reset_index(inplace=True)

    X = features_by_ticker.drop(columns=['ticker'])
    X.replace([np.inf, -np.inf], np.nan, inplace=True)
    X.dropna(inplace=True)

    features_by_ticker = features_by_ticker.loc[X.index]

    X_clipped = X.clip(lower=0)
    X_log = X_clipped.map(np.log1p)

    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X_log)
    print("KMeans Clustering...")
    kmeans = KMeans(n_clusters=4, random_state=42)
    labels = kmeans.fit_predict(X_scaled)
    features_by_ticker['cluster'] = labels

    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    features_by_ticker['PC1'] = X_pca[:, 0]
    features_by_ticker['PC2'] = X_pca[:, 1]
    return features_by_ticker
