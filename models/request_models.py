from pydantic import BaseModel
from typing import List


class Asset(BaseModel):
    ticker: str
    weight: int


class BacktestRequest(BaseModel):
    initial_cash: int
    start_date: str
    end_date: str
    commission: float
    portfolio: List[Asset]


