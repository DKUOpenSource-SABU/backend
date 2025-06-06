import os
import glob
import warnings

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler



# 클러스터링 진행 중 발생하는 numpy 경고 무시
warnings.filterwarnings("ignore", category=RuntimeWarning)

# 최소 1년치의 데이터를 가지고 있는 주식 정보 불러오기
# 작성자 : 김동혁
def read_csv_files_year_filter(tickers=None):
    base_path = os.path.abspath('./data/stock/')
    all_files = glob.glob(os.path.join(base_path, "*.csv"))
    
    # tickers가 주어지면 해당 ticker만 필터링
    if tickers is not None:
        tickers = set(tickers)
        all_files = [f for f in all_files if os.path.splitext(os.path.basename(f))[0] in tickers]
    
    # 데이터 없는 파일 처리
    no_date_files = []
    for file_path in all_files:
        ticker = os.path.splitext(os.path.basename(file_path))[0]
        try:
            # 헤더만 읽어서 컬럼명 확인
            df = pd.read_csv(file_path, nrows=1)
            if 'date' not in df.columns:
                no_date_files.append(file_path)
        except Exception as e:
            print(f"{file_path} 읽기 오류: {e}")

    if no_date_files:
        print("아래 파일들은 데이터가 없습니다:")
        for file in no_date_files:
            print("-", os.path.basename(file))

    df_list = []
    for file_path in all_files:
        if file_path in no_date_files:
            continue  # 데이터 없는 파일은 건너뜀
        ticker = os.path.splitext(os.path.basename(file_path))[0]
        df = pd.read_csv(file_path, parse_dates=['date'])
        # 최소 1년치 데이터 보유 시에만 추가
        if len(df) >= 252:  
            df['ticker'] = ticker   # 티커 컬럼 추가
            df.drop([
                'adjClose', 'adjHigh', 'adjLow', 'adjOpen',
                'adjVolume', 'divCash', 'splitFactor'
            ], axis=1, inplace=True)
            df_list.append(df)
    return df_list


# 모든 종목이 공통으로 가지는 최소 기간 탐색
# 작성자 : 김동혁
def find_shortest_period(df_list):
    min_dates = []
    max_dates = []

    for df in df_list:
        min_dates.append(df['date'].min())
        max_dates.append(df['date'].max())

    # 모든 종목이 공통으로 갖는 기간
    start_date = max(min_dates)
    end_date = max(max_dates)
    return start_date, end_date


# 상장폐지 종목 제거 (마지막 데이터가 최신 데이터가 아닌 과거 데이터)
# 작성자 : 김동혁
def removed_stocks(df_list, end_date):
    # end_date가 존재하지 않는(상장폐지된) 종목 제거
    filtered_df_list = []
    for df in df_list:
        # date 컬럼이 datetime 타입이 아닌 경우 변환
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'])
        # 제일 최신 데이터를 보유하고 있는 경우에만 리스트에 추가
        if end_date in df['date'].values:
            filtered_df_list.append(df)
    return filtered_df_list


# 탐색한 최소 기간의 데이터만 추출
# 작성자 : 김동혁
def same_period(df_list, start_date, end_date):
    trimmed_list = []

    for df in df_list:
        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        trimmed_df = df.loc[mask].copy()
        trimmed_list.append(trimmed_df)
    return trimmed_list


# 가격 정보를 이용한 지표 생성 및 추출
# 작성자 : 김동혁
def extract_features(df):
    # RSI 계산
    def calculate_rsi(series, period=14):
        delta = series.diff()  # 하루 전 대비 가격 변화량
        # 상승폭 평균(오른 날은 양수, 내린 날은 0으로 처리)
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        # 하락폭 평균(내린 날은 양수, 오른 날은 0으로 처리)
        loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
        rs = gain / loss  # 상대 강도
        rsi = 100 - (100 / (1 + rs))  # RSI 공식
        return rsi
    

    # MDD 계산
    def calculate_mdd(series):
        roll_max = series.cummax()  # 누적 최고가 시계열
        drawdown = (series - roll_max) / roll_max
        mdd = drawdown.min()
        return mdd


    # 6개월 지표 계산 (이동평균, 수익률, 변동성)
    def calc_6m_features(df):
        df_6m = df.tail(126)
        ma_6m = df_6m['close'].mean()
        ret_6m = (df_6m['close'].iloc[-1] / df_6m['close'].iloc[0]) - 1
        # 최근 6개월 변동성 (로그수익률 표준편차 × sqrt(252)로 연환산)
        logret = np.log(df_6m['close'] / df_6m['close'].shift(1)).dropna()
        vola_6m = logret.std() * np.sqrt(252)  # 연율화
        return ma_6m, ret_6m, vola_6m

    
    ticker = df['ticker'].unique()[0]
    ma60 = df['close'].rolling(window=60).mean().iloc[-1]  # 60일 이동평균
    ret = (df['close'].iloc[-1] / df['close'].iloc[0]) - 1  # 전체 기간 수익률
    vola = df['close'].pct_change().rolling(window=30).std().mean()  # 30일 변동성
    rsi = calculate_rsi(df['close'], 14).iloc[-1]
    mdd = calculate_mdd(df['close'])
    avg_vol = df['volume'].mean()  # 평균 거래량
    ma_6m, ret_6m, vola_6m = calc_6m_features(df)
    
    return [ticker, ma60, ma_6m, ret, ret_6m, vola, vola_6m, rsi, mdd, avg_vol]


# 추출한 지표를 가지고 데이터프레임 구성 및 결측치 제거
# 작성자 : 김동혁
def make_feature_df(df_list):
    feature_names = [
        'ticker', 'MA_60', 'MA_6M', 'Total_Return', 'Return_6M', 
        'Vol_30', 'Vol_6M', 'RSI_14', 'MDD', 'Avg_Volume'
    ]
    features_list = []

    for df in df_list:
        feats = extract_features(df)
        features_list.append(feats)

    features_df = pd.DataFrame(features_list, columns=feature_names)
    features_df = features_df.dropna()  # 결측치 제거
    return features_df


# Isolation Forest을 이용하여 이상치 탐색
# 작성자 : 김동혁
def find_outlier(df):
    # 각 데이터 포인트가 여러 개의 랜덤 결정 트리에서 고립되는 데 필요한 경로 길이(depth)를 기준으로 이상치 판단
    clf = IsolationForest(contamination=0.05, random_state=42)  # 전체의 5%를 이상치로 간주
    clf.fit(df.drop(columns=['ticker']))
    df['outlier'] = clf.predict(df.drop(columns=['ticker']))
    
    # 정상 데이터
    normal_df = df[df['outlier'] == 1].copy().drop(columns=['outlier'])
    normal_df = normal_df.reset_index(drop=True)
    # 이상치 데이터
    outlier_df = df.loc[df['outlier'] == -1].drop(columns=['outlier'])
    outlier_df = outlier_df.reset_index(drop=True)
    
    return normal_df, outlier_df


# 엘보우 기법을 이용하여 K-Means 클러스터링에 필요한 최적의 k 탐색
# 작성자 : 김동혁
def optimization_k(df):
    inertias = []  # SSE
    for k in range(1, 11):
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(df)
        inertias.append(kmeans.inertia_)
    

    # 엘보우 포인트 자동 탐지 함수
    def find_elbow_point(x, y):
        x1, y1 = x[0], y[0]
        x2, y2 = x[-1], y[-1]
        distances = []
        for i in range(len(x)):
            numerator = abs((y2 - y1)*x[i] - (x2 - x1)*y[i] + x2*y1 - y2*x1)
            denominator = np.sqrt((y2 - y1)**2 + (x2 - x1)**2)
            distances.append(numerator / denominator)
        return np.argmax(distances) + 1  # +1은 K가 1부터 시작할 때
    

    optimal_k = find_elbow_point(np.array(list(range(1, 11))), np.array(inertias))
    return optimal_k


# K-Means 클러스터링 및 시각화에 필요한 정보 2차원 축소
# 작성자 : 김동혁
def k_means(tickers=None):
    df_list = read_csv_files_year_filter(tickers)
    if not df_list:
        print("선택한 티커에 해당하는 데이터가 없습니다.")
        return None
    
    start_date, end_date = find_shortest_period(df_list)
    filtered_df_list = removed_stocks(df_list, end_date)
    trimmed_list = same_period(filtered_df_list, start_date, end_date)
    features_df = make_feature_df(trimmed_list)
    normal_df, outlier_df = find_outlier(features_df)

    # 스케일링
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(normal_df.drop(columns=['ticker']))

    # K-Means 클러스터링
    k = optimization_k(X_scaled)
    kmeans = KMeans(n_clusters=k, random_state=42)
    clusters = kmeans.fit_predict(X_scaled)
    normal_df.loc[:, 'cluster'] = clusters

    # 정상치 데이터 2차원 축소
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    normal_df['PC1'] = X_pca[:, 0]
    normal_df['PC2'] = X_pca[:, 1]
    # 클러스터별 PC1, PC2 평균값
    pca_means = normal_df.groupby('cluster')[['PC1', 'PC2']].mean()

    # 이상치 데이터 스케일링
    outlier_scaled = scaler.transform(outlier_df.drop(columns=['ticker']))

    # 학습된 클러스터링 모델에 이상치 데이터 넣어 분류
    outlier_clusters = kmeans.predict(outlier_scaled)
    outlier_df.loc[:, 'cluster'] = outlier_clusters

    # 이상치 데이터 2차원 축소값 정상치 데이터의 평균값으로 대체
    outlier_df['PC1'] = outlier_df['cluster'].map(pca_means['PC1'])
    outlier_df['PC2'] = outlier_df['cluster'].map(pca_means['PC2'])

    # 정상 데이터, 이상치 데이터 결합
    combined_df = pd.concat([normal_df, outlier_df], axis=0)
    result_df = combined_df[['ticker', 'PC1', 'PC2', 'cluster']]

    return result_df


if __name__ == "__main__":
    k_means()