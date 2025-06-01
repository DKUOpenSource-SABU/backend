from datetime import datetime

def calculate_metrics(raw_result, strategy, rebalance, initial_cash, weights):
    analyzers = raw_result.get("analyzers", {})
    prices = raw_result.get("prices", {})
    portfolio_values = raw_result.get("portfolio_value", [])
    drawdown_series = raw_result.get("drawdown_series", [])
    dates = raw_result.get("dates", [])

    returns = analyzers.get("returns", {})
    drawdown = analyzers.get("drawdown", {})
    annual = analyzers.get("annual", {})

    final_balance = returns.get("rtot", 0.0) * initial_cash + initial_cash
    total_return = returns.get("rtot", 0.0) * 100
    max_drawdown = drawdown.get("max", {}).get("drawdown", 0.0)

    portfolio_growth = [
        {"date": d, "value": v} for d, v in zip(dates, portfolio_values)
    ]

    drawdown_series = [
        {"date": d, "drawdown": dd} for d, dd in zip(dates, drawdown_series)
    ]

    annual_returns = {
        str(k): round(v * 100, 2) for k, v in annual.items()
    }
    if portfolio_growth:
        start_value = portfolio_growth[0]["value"]
        end_value = portfolio_growth[-1]["value"]
        start_date = portfolio_growth[0]["date"]
        end_date = portfolio_growth[-1]["date"]
        cagr = calculate_cagr(start_value, end_value, start_date, end_date) * 100
    else:
        cagr = 0.0

    assets = []
    for ticker, weight in weights.items():
        price_series = prices.get(ticker)
        if not price_series:
            continue
        start_price = price_series[0]
        end_price = price_series[-1]
        return_pct = ((end_price / start_price) - 1) * 100
        initial_investment = initial_cash * weight
        final_value = initial_investment * (end_price / start_price)
        contribution_pct = weight * return_pct

        assets.append({
            "ticker": ticker,
            "weight": weight,
            "start_price": start_price,
            "end_price": end_price,
            "return_pct": return_pct,
            "initial_investment": initial_investment,
            "final_value": final_value,
            "contribution_pct": contribution_pct
        })

    return {
        "strategy": strategy,
        "rebalance": rebalance,
        "initial_balance": initial_cash,
        "final_balance": final_balance,
        "total_return": total_return,
        "cagr": cagr,
        "max_drawdown": round(max_drawdown, 2) * -1,
        "portfolio_growth": portfolio_growth,
        "drawdown_series": drawdown_series,
        "annual_returns": annual_returns,
        "assets": assets
    }

def calculate_cagr(start_value, end_value, start_date_str, end_date_str, fmt="%Y-%m"):
    start = datetime.strptime(start_date_str, fmt)
    end = datetime.strptime(end_date_str, fmt)
    days = (end - start).days
    years = days / 365
    if years <= 0:
        return 0.0
    return (end_value / start_value) ** (1 / years) - 1
