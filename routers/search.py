from fastapi import APIRouter, Body
from typing import List, Optional
from core.db import get_all_tickers

router = APIRouter()

@router.post("/ticker")
async def search_ticker(query: str, clusters: Optional[List[int]] = Body(None, embed=True)):
    all_tickers = get_all_tickers()
    query_upper = query.upper()
    if clusters:
        results = [
            item for symbol, item in all_tickers.items()
            if query_upper in symbol and item["CLUSTER"] in clusters
        ][:50]
    else:
        results = [
            item for symbol, item in all_tickers.items()
            if query_upper in symbol
        ][:50]

    return {"results": results}

@router.get("/cluster")
def search_by_cluster(clusterId: int):
    pass
