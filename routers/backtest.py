from fastapi import APIRouter
from models.request_models import BacktestRequest
from models.response_models import BacktestResponse
from backtest.backtest_runner import run_backtest
from core.db import get_max_strategy

router = APIRouter()

@router.post("/", response_model=BacktestResponse)
def backtest(req: BacktestRequest):
    return run_backtest(req)

@router.get("/leaderboard")
def leaderboard():
    return {"leaderboard": get_max_strategy()}
