import backtrader as bt


class RsiStrategy(bt.Strategy):
    params = dict(period=14, overbought=70, oversold=30, rebalance_mode="none")

    def __init__(self):
        self.rsis = {
            data._name: bt.ind.RSI(data.close, period=self.p.period)
            for data in self.datas
        }
        self.last_rebalance = None
        self.first_run = True

    def next(self):
        dt = self.datas[0].datetime.date(0)

        if self.p.rebalance_mode == "none":
            if self.first_run:
                self.rebalance_portfolio()
                self.first_run = False

        elif self.p.rebalance_mode == "monthly":
            if not self.last_rebalance or dt.month != self.last_rebalance.month:
                self.rebalance_portfolio()
                self.last_rebalance = dt

        elif self.p.rebalance_mode == "quarterly":
            if (
                not self.last_rebalance
                or (dt.month - 1) // 3 != (self.last_rebalance.month - 1) // 3
            ):
                self.rebalance_portfolio()
                self.last_rebalance = dt

    def rebalance_portfolio(self):
        for data in self.datas:
            rsi = self.rsis[data._name]
            pos = self.getposition(data).size

            if rsi[0] < self.p.oversold and pos == 0:
                size = self.broker.get_cash() / len(self.datas) / data.close[0]
                self.buy(data=data, size=size)
            elif rsi[0] > self.p.overbought and pos > 0:
                self.close(data=data)


class Rsi:
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

            cerebro.addstrategy(RsiStrategy, rebalance_mode=mode)

            # Add analyzers
            cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
            cerebro.addanalyzer(
                bt.analyzers.TimeReturn, _name="timereturn", timeframe=bt.TimeFrame.Years
            )
            cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
            cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name="annual")

            result = cerebro.run()[0]

            analyzers = {
                "returns": result.analyzers.returns.get_analysis(),
                "timereturn": result.analyzers.timereturn.get_analysis(),
                "drawdown": result.analyzers.drawdown.get_analysis(),
                "annual": result.analyzers.annual.get_analysis(),
            }

            portfolio_value = [result.broker.get_value()]

            results.append({
                "strategy": "rsi",
                "rebalance": mode,
                "portfolio_value": portfolio_value,
                "dates": dates,
                "prices": prices,
                "analyzers": analyzers,
            })

        return results
