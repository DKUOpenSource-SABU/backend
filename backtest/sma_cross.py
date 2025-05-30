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
        self.monthly_values = {}
        self.last_month = None
        self.monthly_drawdown = {}
        self.month_peak = {}


    def next(self):
        dt = self.datas[0].datetime.date(0)
        current_month = dt.strftime('%Y-%m')
        value = self.broker.getvalue()

        if current_month != self.last_month:
            if self.last_month is not None:
                peak = self.month_peak.get(self.last_month, value)
                drawdown = (value - peak) / peak * 100 if peak > 0 else 0.0
                self.monthly_drawdown[self.last_month] = round(drawdown, 2)

            self.monthly_values[current_month] = value
            self.month_peak[current_month] = value
            self.last_month = current_month
        else:
            self.month_peak[current_month] = max(self.month_peak.get(current_month, value), value)

        if not hasattr(self, 'rebalanced'):
            self.rebalance_portfolio()
            self.rebalanced = True

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


    def stop(self):
        if self.last_month and self.last_month not in self.monthly_drawdown:
            value = self.broker.get_value()
            peak = self.month_peak.get(self.last_month, value)
            drawdown = (value - peak) / peak * 100 if peak > 0 else 0.0
            self.monthly_drawdown[self.last_month] = round(drawdown, 2)


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

            cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
            cerebro.addanalyzer(
                bt.analyzers.TimeReturn, _name="timereturn", timeframe=bt.TimeFrame.Years
            )
            cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
            cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name="annual")

            result = cerebro.run()[0]
            monthly_values = result.monthly_values
            monthly_drawdown = result.monthly_drawdown

            sorted_months = sorted(monthly_values.keys())
            portfolio_value = [monthly_values[m] for m in sorted_months]
            drawdown_series = [monthly_drawdown[m] for m in sorted_months]
            dates = sorted_months

            analyzers = {
                "returns": result.analyzers.returns.get_analysis(),
                "timereturn": result.analyzers.timereturn.get_analysis(),
                "drawdown": result.analyzers.drawdown.get_analysis(),
                "annual": result.analyzers.annual.get_analysis(),
            }

            results.append({
                "strategy": "Sma Cross",
                "rebalance": mode,
                "portfolio_value": portfolio_value,
                "drawdown_series": drawdown_series,
                "dates": dates,
                "prices": prices,
                "analyzers": analyzers,
            })

        return results
