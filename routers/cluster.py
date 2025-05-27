from fastapi import APIRouter
from fastapi.responses import JSONResponse
from models.schemas import TickerList
from clustering.kmeans_module import *
import matplotlib

from core.db import get_pretrained_data, get_hull_list, get_tickers_by_symbol
import clustering.recommend

matplotlib.use('Agg')
router = APIRouter()


# ---------- Clustering 관련 API ----------

# 분석된 클러스터링 기법을 활용하여 PC1, PC2, Convex Hull 좌표를 반환하는 API
# 작성자 : 김태형
@router.post("/analyze")
def cluster_analyze(pre: str, data: TickerList):
    df = get_pretrained_data()
    PC1 = df["PC1"]
    PC2 = df["PC2"]
    hull_list = get_hull_list()
    nodes = df[df["ticker"].isin(data.tickers)].to_dict(orient="records")
    res = {
        "nodes" : nodes,
        "hull_coords": hull_list
    }
    return res

# Ticker 추천 API
# 클러스터링 결과를 기반으로 추천 티커를 반환하는 API
# 작성자 : 김태형
@router.post("/recommend")
def recommend(data: TickerList):
    top5_tickers = clustering.recommend.recommend(data.tickers)
    if top5_tickers is None or top5_tickers.empty:
        return JSONResponse(status_code=404,
                            content={"error": "No recommendations found."})
    res = get_tickers_by_symbol(top5_tickers["ticker"].tolist())
    if not res:
        return JSONResponse(status_code=404,
                            content={"error": "No recommendations found."})
    return [item for symbol, item in res.items()][:50]
