from backtest.buy_and_hold import BuyAndHold
from backtest.sma_cross import SmaCross
from backtest.rsi import RSI
from backtest.data_provider import load_data
from backtest.utils import calculate_metrics
from models.request_models import BacktestRequest
from datetime import datetime
from core.db import update_max_strategy
import copy

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
                continue
            strategy = StrategyClass(data, weights, req.initial_cash)
            raw_results = strategy.run()
            max_total_return = float("-inf")
            for raw_result in raw_results:
                metrics = calculate_metrics(
                    raw_result,
                    strategy=raw_result["strategy"],
                    rebalance=raw_result["rebalance"],
                    initial_cash=req.initial_cash,
                    weights=weights
                )
                results.append(metrics)
                if metrics["total_return"] > max_total_return:
                    max_total_return = max(max_total_return, metrics["total_return"])
                    max_strategy = copy.deepcopy(metrics)
                    max_strategy.pop("portfolio_growth", None)
                    max_strategy.pop("drawdown_series", None)
                    max_strategy.pop("annual_returns", None)
                    update_max_strategy(max_total_return, max_strategy)
        except ValueError as e:
            results.append({
                "strategy": StrategyClass.__name__,
                "error": str(e)
            })

    return {"results": results}
