import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from clustering.kmeans_module import *



def read_stock_sector():
    ticker_stock = pd.read_csv('./data/ticker_stock.csv')
    ticker_stock = ticker_stock.dropna()
    ticker_stock = ticker_stock.rename(columns={
        'Symbol': 'ticker', 'Sector': 'sector'})
    return ticker_stock


def sector_info_merge(df, sector_df):
    merged_df = pd.merge(
        df, 
        sector_df[['ticker', 'sector']], 
        on='ticker', 
        how='left'
    )
    # 섹터 정보 없는 경우 제거
    merged_df = merged_df.dropna().reset_index(drop=True)
    # 기타 섹터 제거
    merged_df = merged_df[merged_df['sector'] != 'Miscellaneous']
    # 티커 열 필요 없으므로 제거
    merged_df = merged_df.drop(columns=['ticker'])

    return merged_df


# 이상치 제거 함수 (IQR 방식)
def grouped_sector(df):
    def remove_outliers(df):
        columns = df.columns.tolist()
        for col in columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
        return df
    
    
    filtered_df = df.groupby('sector').apply(
        lambda x: remove_outliers(x)
        ).reset_index()
    filtered_df = filtered_df.drop(columns=['level_1'])
    return filtered_df


def sector_col_avg(df):
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    avg_df = df.groupby('sector')[numeric_cols].mean().reset_index()

    return avg_df


def sector_visualization():
    df_list = read_csv_files_year_filter()
    start_date, end_date = find_shortest_period(df_list)
    filtered_df_list = removed_stocks(df_list, end_date)
    trimmed_list = same_period(filtered_df_list, start_date, end_date)
    features_df = make_feature_df(trimmed_list)
    
    sector_df = read_stock_sector()
    merged_df = sector_info_merge(features_df, sector_df)
    filtered_df = grouped_sector(merged_df)
    avg_df = sector_col_avg(filtered_df)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(avg_df.drop(columns=['sector']))

    # PCA 2차원 축소
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)

    # 결과를 데이터프레임에 추가
    avg_df['PC1'] = X_pca[:, 0]
    avg_df['PC2'] = X_pca[:, 1]

    # if __name__ == "__main__":
    #     '''지워도 되는 부분'''
    #     # Sector별 색상 지정
    #     sector_colors = {
    #         'Industrials': '#1f77b4',           # 파랑
    #         'Real Estate': '#2ca02c',           # 초록
    #         'Finance': '#d62728',               # 빨강
    #         'Technology': '#9467bd',            # 보라
    #         'Health Care': '#8c564b',           # 갈색
    #         'Consumer Staples': '#e377c2',      # 핑크
    #         'Consumer Discretionary': '#7f7f7f',# 회색
    #         'Energy': '#bcbd22',                # 올리브
    #         'Utilities': '#aec7e8',             # 밝은 파랑
    #         'Basic Materials': '#ffbb78',       # 밝은 오렌지
    #         'Telecommunications': '#98df8a'     # 밝은 초록
    #     }

    #     plt.figure(figsize=(8, 6))
    #     for sector, color in sector_colors.items():
    #         subset = avg_df[avg_df['sector'] == sector]
    #         plt.scatter(subset['PC1'], subset['PC2'], label=sector, color=color, s=100, alpha=0.7)

    #     plt.xlabel('PC1')
    #     plt.ylabel('PC2')
    #     plt.title('Sector Distribution')
    #     plt.legend()
    #     plt.grid(True)
    #     plt.show()

    return avg_df[['sector', 'PC1', 'PC2']]