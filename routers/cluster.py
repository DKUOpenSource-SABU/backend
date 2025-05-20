from fastapi import APIRouter
from fastapi.responses import JSONResponse
from models.schemas import TickerList
from clustering.Kmeans import *
from core.db import get_pretrained_data, get_hull_list
import numpy as np
import io
import matplotlib

matplotlib.use('Agg')
router = APIRouter()

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

@router.post("/recommend")
def recommend(data: TickerList):
    return {
        "recommendations": ["NVDA", "MSFT"]  # 더미 추천
    }
