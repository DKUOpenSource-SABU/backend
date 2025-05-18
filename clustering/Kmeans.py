from clustering import utils
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

def k_means(tickers):
    df = utils.read_csv_files()
    start_date = min(df[df['ticker'].isin(tickers)].date)
    end_date = max(df[df['ticker'].isin(tickers)].date)

    min_dates = df.groupby('ticker')['date'].min()
    latest_start = min_dates.max()
    df = df[df['date'] >= latest_start]
    #df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    features_by_ticker = (
    df.groupby('ticker')
    .agg({
        'close': ['mean', 'std'],
        'volume': 'mean',
        'divCash': 'sum',
        'splitFactor': 'sum'
    })
)
    features_by_ticker.columns = ['_'.join(col).strip() for col in features_by_ticker.columns.values]
    features_by_ticker.reset_index(inplace=True)

    X = features_by_ticker.drop(columns=['ticker'])
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=4, random_state=42)
    labels = kmeans.fit_predict(X_scaled)
    features_by_ticker['cluster'] = labels

    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    features_by_ticker['PC1'] = X_pca[:, 0]
    features_by_ticker['PC2'] = X_pca[:, 1]
    return features_by_ticker