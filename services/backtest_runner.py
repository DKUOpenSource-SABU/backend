from app.strategies.buy_and_hold import BuyAndHold
from app.strategies.sma_cross import SmaCross
from app.strategies.rsi import RSI
from app.services.data_provider import load_data
from app.utils.calculate_metrics import calculate_metrics
from app.models.request_models import BacktestRequest
from datetime import datetime
STRATEGY_MIN_DAYS = {
    "RSI": 14,
    "SmaCross": 50,
    "BuyAndHold": 1
}

STRATEGIES = [BuyAndHold, SmaCross, RSI]

def run_backtest(req: BacktestRequest):
    tickers = [asset.ticker for asset in req.portfolio]
    weights = {asset.ticker: asset.weight / 100 for asset in req.portfolio}
    data = load_data(tickers, req.start_date, req.end_date)
    start = datetime.strptime(req.start_date, "%Y-%m-%d")
    end = datetime.strptime(req.end_date, "%Y-%m-%d")
    date_diff = (end - start).days

    results = []

    for StrategyClass in STRATEGIES:
        try:
            required_days = STRATEGY_MIN_DAYS[StrategyClass.__name__]
            if date_diff < required_days:
                raise ValueError(
                    f"{StrategyClass.__name__} 전략은 최소 {required_days}일 이상의 데이터가 필요합니다. 현재 기간: {date_diff}일")
            strategy = StrategyClass(data, weights, req.initial_cash)
            raw_results = strategy.run()
            for raw_result in raw_results:
                metrics = calculate_metrics(
                    raw_result,
                    strategy=raw_result["strategy"],
                    rebalance=raw_result["rebalance"],
                    initial_cash=req.initial_cash,
                    weights=weights
                )
                results.append(metrics)
        except ValueError as e:
            results.append({
                "strategy": StrategyClass.__name__,
                "error": str(e)
            })

    return {"results": results}
