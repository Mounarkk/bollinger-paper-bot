import pandas as pd


def max_drawdown(equity: pd.Series) -> float:
    """Worst drop from a previous peak, as a negative fraction (-0.25 means -25%)."""
    if equity.empty:
        return 0.0
    return float((equity / equity.cummax() - 1).min())


def summarize(equity: pd.Series, trades: list, prices: pd.Series) -> dict:
    sells = [t for t in trades if t.side == "SELL"]
    wins = [t for t in sells if t.pnl > 0]
    return {
        "total_return": float(equity.iloc[-1] / equity.iloc[0] - 1),
        "buy_and_hold_return": float(prices.iloc[-1] / prices.iloc[0] - 1),
        "max_drawdown": max_drawdown(equity),
        "trades": len(trades),
        "closed_positions": len(sells),
        "win_rate": len(wins) / len(sells) if sells else None,
        "fees_paid": float(sum(t.fee for t in trades)),
    }
