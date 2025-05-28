import backtrader as bt
import math
class BuyAndHoldStrategy(bt.Strategy):
    params = (('weights', None), ('rebalance_mode', 'none'),)

    def __init__(self):
        self.rebalanced = False

    def next(self):
        if not self.rebalanced:
            total_cash = self.broker.get_cash()
            for data in self.datas:
                ticker = data._name
                weight = self.p.weights.get(ticker, 0)
                if weight <= 0:
                    continue
                price = data.close[0]
                alloc_cash = total_cash * weight
                size = int(alloc_cash / price)
                self.buy(data=data, size=size)
            self.rebalanced = True


class BuyAndHold:
    def __init__(self, data, weights, initial_cash):
        self.data = data
        self.weights = weights
        self.initial_cash = initial_cash

    def run(self):
        results = []
        for mode in ["none", "monthly", "quarterly"]:
            cerebro = bt.Cerebro()
            cerebro.broker.set_coc(True)
            cerebro.broker.set_cash(self.initial_cash)

            prices = {}
            dates = None

            for ticker, df in self.data.items():
                datafeed = bt.feeds.PandasData(dataname=df)
                cerebro.adddata(datafeed, name=ticker)
                prices[ticker] = df["Close"].tolist()
                if dates is None:
                    dates = df.index.strftime("%Y-%m-%d").tolist()

            cerebro.addstrategy(BuyAndHoldStrategy, rebalance_mode=mode, weights=self.weights)

            cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
            cerebro.addanalyzer(bt.analyzers.TimeReturn, _name="timereturn", timeframe=bt.TimeFrame.Years)
            cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
            cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name="annual")

            result = cerebro.run()[0]

            annual = result.analyzers.annual.get_analysis()

            analyzers = {
                "returns": result.analyzers.returns.get_analysis(),
                "timereturn": result.analyzers.timereturn.get_analysis(),
                "drawdown": result.analyzers.drawdown.get_analysis(),
                "annual": annual,
            }

            portfolio_value = [result.broker.get_value()]

            results.append({
                "strategy": "buy_and_hold",
                "rebalance": mode,
                "portfolio_value": portfolio_value,
                "dates": dates,
                "prices": prices,
                "analyzers": analyzers,
            })

        return results