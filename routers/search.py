from fastapi import APIRouter, Body
from typing import List, Optional
import api.tiingo as tiingo
import api.finBERT as finbert

from core.db import get_all_tickers

router = APIRouter()

# ---------- Ticker 관련 API ----------

# Ticker 검색 API
# 클러스터 필터링을 지원하며, 최대 50개의 결과를 반환합니다.
# 작성자 : 김태형
@router.post("/ticker")
async def search_ticker(query: str, 
                        clusters: Optional[List[int]] = Body(None, embed=True)):
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

# Ticker의 일간 데이터를 가져오는 API
# 작성자 : 김태형
@router.get("/ticker/daily")
async def get_ticker_data_daily(ticker: str):
    ticker = ticker.upper()
    data = tiingo.get_ticker_data_daily(ticker)
    if data is None:
        return {"error": "Ticker not found"}
    return data

# Ticker의 주간 데이터를 가져오는 API
# 작성자 : 김태형
@router.get("/ticker/weekly")
async def get_ticker_data_weekly(ticker: str):
    ticker = ticker.upper()
    data = tiingo.get_ticker_data_weekly(ticker)
    if data is None:
        return {"error": "Ticker not found"}
    return data

# Ticker의 월간 데이터를 가져오는 API
# 작성자 : 김태형
@router.get("/ticker/monthly")
async def get_ticker_data_monthly(ticker: str):
    ticker = ticker.upper()
    data = tiingo.get_ticker_data_monthly(ticker)
    if data is None:
        return {"error": "Ticker not found"}
    return data

# Ticker의 연간 데이터를 가져오는 API
# 작성자 : 김태형
@router.get("/ticker/annual")
async def get_ticker_data_annual(ticker: str):
    ticker = ticker.upper()
    data = tiingo.get_ticker_data_annual(ticker)
    if data is None:
        return {"error": "Ticker not found"}
    return data

# Ticker의 메타데이터를 가져오는 API
# 작성자 : 김태형
@router.get("/ticker/meta")
async def get_ticker_data_meta(ticker: str):
    ticker = ticker.upper()
    data = tiingo.get_ticker_data(ticker)
    if data is None:
        return {"error": "Ticker not found"}
    return data

# Ticker의 뉴스 데이터를 가져오는 API
# 작성자 : 김태형
@router.get("/ticker/news")
async def get_ticker_news(ticker: str):
    ticker = ticker.upper()
    data = tiingo.get_ticker_news(ticker)
    if data is None:
        return {"error": "Ticker not found"}
    for item in data:
        item["semantic"] = finbert.semantic_analysis(item["title"])[0]["label"]
    return data
