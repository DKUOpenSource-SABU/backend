from fastapi import APIRouter
from models.request_models import BacktestRequest
from models.response_models import BacktestResponse
from backtest.backtest_runner import run_backtest
from core.db import get_max_strategy

router = APIRouter()

@router.post("/", response_model=BacktestResponse)
def backtest(req: BacktestRequest):
    if not req.portfolio or len(req.portfolio) < 2:
        return {"error": "Portfolio must contain at least 2 assets."}
    if not req.start_date or not req.end_date:
        return {"error": "Start date and end date are required."}
    if req.start_date >= req.end_date:
        return {"error": "Start date must be before end date."}
    if req.initial_cash <= 0:
        return {"error": "Initial cash must be greater than 0."}
    if not req.portfolio or len(req.portfolio) < 2:
        return {"error": "Portfolio must contain at least 2 assets."}
    if not all(asset.ticker for asset in req.portfolio):
        return {"error": "All assets in the portfolio must have a ticker."}
    if not all(0 < asset.weight <= 100 for asset in req.portfolio):
        return {"error": "All asset weights must be between 0 and 100."}
    if sum(asset.weight for asset in req.portfolio) != 100:
        return {"error": "Total portfolio weight must equal 100%."}
    try:
        res = run_backtest(req)
    except Exception as e:
        return {"error": str(e)}
    return res

@router.get("/leaderboard")
def leaderboard():
    return {"leaderboard": get_max_strategy()}
