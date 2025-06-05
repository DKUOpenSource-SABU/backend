import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

import core.db

# 티커별 섹터 정보 데이터프레임 반환
# 작성자 : 김동혁
def read_stock_sector():
    ticker_stock = pd.read_csv('./data/ticker_stock.csv')
    ticker_stock = ticker_stock.dropna()
    ticker_stock = ticker_stock.rename(
        columns={'Symbol': 'ticker', 'Sector': 'sector'}
    )
    return ticker_stock

# 섹터 정보 병합
# 작성자 : 김동혁
def sector_info_merge(df, sector_df):
    merged_df = pd.merge(
        df, sector_df[['ticker', 'sector']], on='ticker', how='left'
    )
    # 섹터 정보 없는 경우 제거
    merged_df = merged_df.dropna().reset_index(drop=True)
    # 기타 섹터 제거
    merged_df = merged_df[merged_df['sector'] != 'Miscellaneous']
    merged_df = merged_df.drop(columns=['ticker'])
    return merged_df

# 섹터별 이상치 제거 함수
# 작성자 : 김동혁
def grouped_sector(df):
    # IQR 방식 이상치 제거
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

# 섹터별 feature 평균값 계산
# 작성자 : 김동혁
def sector_col_avg(df):
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    avg_df = df.groupby('sector')[numeric_cols].mean().reset_index()
    return avg_df

# 섹터별 2차원 축소 시각화 정보 반환
# 작성자 : 김동혁
def sector_visualization():
    features_df = core.db.get_pretrained_feature()
    
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

    return avg_df[['sector', 'PC1', 'PC2']]