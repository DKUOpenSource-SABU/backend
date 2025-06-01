import backtrader as bt

class BuyAndHoldStrategy(bt.Strategy):
    params = (('weights', None), ('rebalance_mode', 'none'),)

    def __init__(self):
        self.last_rebalance = None
        self.monthly_values = {}
        self.monthly_drawdown = {}
        self.month_peak = {}
        self.last_month = None


    def next(self):
        current_date = self.datas[0].datetime.date(0)
        current_month = current_date.strftime("%Y-%m")
        value = self.broker.get_value()
        dt = self.datas[0].datetime.date(0)
        
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

        if self.p.rebalance_mode == "monthly":
            if not self.last_rebalance or dt.month != self.last_rebalance.month:
                self.rebalance_portfolio()
                self.last_rebalance = dt

        elif self.p.rebalance_mode == "quarterly":
            if not self.last_rebalance or (dt.month - 1) // 3 != (self.last_rebalance.month - 1) // 3:
                self.rebalance_portfolio()
                self.last_rebalance = dt

    def rebalance_portfolio(self):
        total_value = self.broker.get_value()
        for data in self.datas:
            ticker = data._name
            weight = self.p.weights.get(ticker, 0)
            if weight <= 0:
                continue

            self.close(data=data)

            price = data.close[0]
            alloc_cash = total_value * weight
            size = int(alloc_cash / price)
            self.buy(data=data, size=size)


    def stop(self):
        if self.last_month and self.last_month not in self.monthly_drawdown:
            value = self.broker.get_value()
            peak = self.month_peak.get(self.last_month, value)
            drawdown = (value - peak) / peak * 100 if peak > 0 else 0.0
            self.monthly_drawdown[self.last_month] = round(drawdown, 2)


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
            cerebro.addanalyzer(bt.analyzers.TimeReturn, _name="timereturn", timeframe=bt.TimeFrame.Days, fund=True)
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
                "strategy": "Buy and Hold",
                "rebalance": mode,
                "portfolio_value": portfolio_value,
                "drawdown_series": drawdown_series,
                "dates": dates,
                "prices": prices,
                "analyzers": analyzers,
            })

        return results