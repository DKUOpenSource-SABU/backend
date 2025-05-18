import pandas as pd
from clustering.Kmeans import *
import os

df = pd.read_csv('./collect/ticker.csv', encoding='utf-8')
df = df.drop("1 yr % CHANGE", axis=1)

pretrained_data = k_means(df['SYMBOL'][:-1].tolist())
cluster_map = pretrained_data.set_index("ticker")["cluster"].to_dict()

def get_all_tickers():
    global df
    df_trimmed = df.iloc[:-1]
    return {
        row["SYMBOL"]: {
            **row,
            "CLUSTER": cluster_map.get(row["SYMBOL"], None)  # SYMBOL → ticker 매핑
        }
        for row in df_trimmed.to_dict(orient="records")
    }

def get_pretrained_data():
    global pretrained_data
    return pretrained_data