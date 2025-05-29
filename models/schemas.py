from pydantic import BaseModel
from typing import List

# Ticker 데이터 모델 정의
# 작성자 : 김태형
class TickerList(BaseModel):
    tickers: List[str]

class TickerInfo(BaseModel):
    ticker: str
    ratio: float

class RatioList(BaseModel):
    ratios: List[TickerInfo]