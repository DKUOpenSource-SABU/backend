from backtest.buy_and_hold import BuyAndHold
from backtest.sma_cross import SmaCross
from backtest.rsi import Rsi
from backtest.data_provider import load_data
from backtest.utils import calculate_metrics
from models.request_models import BacktestRequest

STRATEGIES = [BuyAndHold, SmaCross, Rsi]

def run_backtest(req: BacktestRequest):
    tickers = [asset.ticker for asset in req.portfolio]
    weights = {asset.ticker: asset.weight / 100 for asset in req.portfolio}
    data = load_data(tickers, req.start_date, req.end_date)

    results = []
    for StrategyClass in STRATEGIES:
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

    return {"results": results}
