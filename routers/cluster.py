from fastapi import APIRouter
from fastapi.responses import JSONResponse
from models.schemas import TickerList
from clustering.Kmeans import *
from scipy.spatial import ConvexHull
from core.db import get_pretrained_data
import numpy as np
import io
import matplotlib

matplotlib.use('Agg')
router = APIRouter()

@router.post("/analyze")
def cluster_analyze(pre: str, data: TickerList):
    if pre == "true":
        df = get_pretrained_data()
    else:
        df = k_means(data.tickers)
    PC1 = df["PC1"]
    PC2 = df["PC2"]
    hull_list = []
    for cluster in df["cluster"].unique().tolist():
        # Convex Hull을 사용하여 클러스터링
        cluster_points = df[df["cluster"] == cluster]
        if len(cluster_points) < 3:
            continue
        points = cluster_points[["PC1", "PC2"]].values
        hull = ConvexHull(points)
        ordered = np.append(hull.vertices, hull.vertices[0])
        hull_coords = [{"x": float(points[i][0]), "y": float(points[i][1])} for i in ordered]
        hull_list.append({
            "cluster": int(cluster),
            "hull_coords" : hull_coords,
            })
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
