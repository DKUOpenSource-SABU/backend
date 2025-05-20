from fastapi import APIRouter, Body
from typing import List, Optional
from core.db import get_all_tickers
import api.tiingo as tiingo

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

@router.get("/ticker/daily")
async def get_ticker_data_daily(ticker: str):
    ticker = ticker.upper()
    data = tiingo.get_ticker_data_daily(ticker)
    if data is None:
        return {"error": "Ticker not found"}
    return data

@router.get("/ticker/weekly")
async def get_ticker_data_weekly(ticker: str):
    ticker = ticker.upper()
    data = tiingo.get_ticker_data_weekly(ticker)
    if data is None:
        return {"error": "Ticker not found"}
    return data

@router.get("/ticker/monthly")
async def get_ticker_data_monthly(ticker: str):
    ticker = ticker.upper()
    data = tiingo.get_ticker_data_monthly(ticker)
    if data is None:
        return {"error": "Ticker not found"}
    return data

@router.get("/ticker/annual")
async def get_ticker_data_annual(ticker: str):
    ticker = ticker.upper()
    data = tiingo.get_ticker_data_annual(ticker)
    if data is None:
        return {"error": "Ticker not found"}
    return data

@router.get("/ticker/meta")
async def get_ticker_data_meta(ticker: str):
    ticker = ticker.upper()
    data = tiingo.get_ticker_data(ticker)
    if data is None:
        return {"error": "Ticker not found"}
    return data

@router.get("/ticker/news")
async def get_ticker_news(ticker: str):
    ticker = ticker.upper()
    data = tiingo.get_ticker_news(ticker)
    if data is None:
        return {"error": "Ticker not found"}
    return data

@router.get("/cluster")
def search_by_cluster(clusterId: int):
    pass
