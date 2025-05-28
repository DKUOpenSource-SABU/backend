import backtrader as bt


class SmaCrossStrategy(bt.Strategy):
    params = dict(fast=20, slow=50, rebalance_mode="none")

    def __init__(self):
        self.smas = {
            data._name: (
                bt.ind.SMA(data.close, period=self.p.fast),
                bt.ind.SMA(data.close, period=self.p.slow),
            )
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
            fast, slow = self.smas[data._name]
            pos = self.getposition(data).size

            if fast[0] > slow[0] and pos == 0:
                size = self.broker.get_cash() / len(self.datas) / data.close[0]
                self.buy(data=data, size=size)
            elif fast[0] < slow[0] and pos > 0:
                self.close(data=data)


class SmaCross:
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

            cerebro.addstrategy(SmaCrossStrategy, rebalance_mode=mode)

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
                "strategy": "sma_cross",
                "rebalance": mode,
                "portfolio_value": portfolio_value,
                "dates": dates,
                "prices": prices,
                "analyzers": analyzers,
            })

        return results