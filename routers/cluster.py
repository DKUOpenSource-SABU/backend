from fastapi import APIRouter
from fastapi.responses import JSONResponse
from models.schemas import TickerList
from models.schemas import RatioList
from clustering.kmeans_module import *
import matplotlib

from core.db import get_pretrained_data, get_hull_list, get_tickers_by_symbol, get_pretrained_sectors
import clustering.recommend
from clustering.diversification_score import diversification_score_mixed

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
    if data is None or not isinstance(data, TickerList):
        return JSONResponse(status_code=400,
                            content={"error": "Invalid input data."})
    if data.tickers is None or len(data.tickers) < 0:
        return JSONResponse(status_code=204,
                            content={"empty": "No Recommendation."})
    if len(data.tickers) < 4:
        return JSONResponse(status_code=400,
                            content={"error": "You have to select at least 4 tickers."})
    try:
        top5_tickers = clustering.recommend.recommend(data.tickers)
    except Exception as e:
        return JSONResponse(status_code=500,
                            content={"error": str(e)})
    if top5_tickers is None:
        return JSONResponse(status_code=404,
                            content={"error": "No recommendations found."})
    res = get_tickers_by_symbol(top5_tickers)
    if not res:
        return JSONResponse(status_code=404,
                            content={"error": "No recommendations found."})
    return [item for symbol, item in res.items()][:50]

@router.get("/sectors")
def sector_analyze():
    sectors_anlyze = get_pretrained_sectors()
    if sectors_anlyze is None or sectors_anlyze.empty:
        return JSONResponse(status_code=404,
                            content={"error": "No sector analysis found."})
    res = {
        "sectors": sectors_anlyze.to_dict(orient="records")
    }
    return res

@router.post("/score")
def score(data: RatioList):
    df = get_pretrained_data()
    selected_tickers = [item.ticker for item in data.ratios]
    weights = {item.ticker: item.ratio / 100 for item in data.ratios}
    
    # 클러스터 분포 기반 점수화
    cluster_score = diversification_score_mixed(df, selected_tickers, weights)
    
    if cluster_score is None:
        return JSONResponse(status_code=400,
                            content={"error": "You Have to select at least 4 tickers."})
    
    return {
        "cluster_score": cluster_score
    }