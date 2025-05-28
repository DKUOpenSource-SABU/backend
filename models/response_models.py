from pydantic import BaseModel
from typing import List, Dict


class PortfolioPoint(BaseModel):
    date: str
    value: float

class DrawdownPoint(BaseModel):
    date: str
    drawdown: float

class AssetResult(BaseModel):
    ticker: str
    weight: float
    start_price: float
    end_price: float
    return_pct: float
    initial_investment: float
    final_value: float
    contribution_pct: float

class StrategyResult(BaseModel):
    strategy: str
    rebalance: str
    initial_balance: float
    final_balance: float
    total_return: float
    cagr: float
    max_drawdown: float
    portfolio_growth: List[PortfolioPoint]
    drawdown_series: List[DrawdownPoint]
    annual_returns: Dict[str, float]
    assets: List[AssetResult]

class BacktestResponse(BaseModel):
    results: List[StrategyResult]
