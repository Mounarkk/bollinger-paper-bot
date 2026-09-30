def plot_backtest(result, strategy, path: str):
    """Saves a chart with the price, bands and trades on top, and the account value below."""
    import matplotlib
    matplotlib.use("Agg")  # no window, just the file
    import matplotlib.pyplot as plt

    data, equity = result.data, result.equity
    bands = strategy.compute_bands(data)
    buys = [t for t in result.trades if t.side == "BUY"]
    sells = [t for t in result.trades if t.side == "SELL"]
    buy_and_hold = data["close"] / data["close"].iloc[0] * equity.iloc[0]

    fig, (price_ax, equity_ax) = plt.subplots(
        2, 1, figsize=(12, 7), sharex=True, gridspec_kw={"height_ratios": [3, 2]}
    )

    price_ax.plot(data.index, data["close"], color="#333333", linewidth=1, label="Close")
    price_ax.fill_between(data.index, bands["lower_band"], bands["upper_band"],
                          color="#4c72b0", alpha=0.15, label="Bands")
    price_ax.scatter([t.timestamp for t in buys], [t.price for t in buys],
                     marker="^", color="#2a9d4a", s=40, zorder=3, label="Buy")
    price_ax.scatter([t.timestamp for t in sells], [t.price for t in sells],
                     marker="v", color="#d1495b", s=40, zorder=3, label="Sell")
    price_ax.set_title(f"{result.symbol} mean reversion backtest")
    price_ax.set_ylabel("Price")
    price_ax.legend(loc="upper left")

    equity_ax.plot(equity.index, equity, color="#4c72b0", label="Strategy")
    equity_ax.plot(buy_and_hold.index, buy_and_hold, color="#999999", linestyle="--", label="Buy and hold")
    equity_ax.set_ylabel("Account value")
    equity_ax.legend(loc="upper left")

    for ax in (price_ax, equity_ax):
        ax.grid(alpha=0.3)
        ax.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
