from fastapi import APIRouter
from app.models.request_models import BacktestRequest
from app.models.response_models import BacktestResponse
from app.services.backtest_runner import run_backtest
from app.services.data_provider import load_data


router = APIRouter()

@router.post("/backtest", response_model=BacktestResponse)
def backtest(req: BacktestRequest):
    return run_backtest(req)

