import utils
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA



def k_means():
    df = utils.read_csv_files()
    start_date = "2020-01-01"
    end_date = "2023-12-31"
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
    features_by_ticker.columns = ['_'.join(col).strip() for col in features_by_ticker.columns.values]
    features_by_ticker.reset_index(inplace=True)

    X = features_by_ticker.drop(columns=['ticker'])
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=4, random_state=42)
    labels = kmeans.fit_predict(X_scaled)

    features_by_ticker['cluster'] = labels
    print(features_by_ticker[['ticker', 'cluster']].sort_values(by='cluster'))

    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)

    plt.figure(figsize=(8,6))
    plt.scatter(X_pca[:, 0], X_pca[:, 1], c=labels, cmap='tab10')
    plt.title("ETF Cluster Visualization (PCA)")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.show()

k_means()