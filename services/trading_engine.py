import logging
from dataclasses import dataclass

import pandas as pd

from services.metrics import summarize

logger = logging.getLogger(__name__)


@dataclass
class BacktestResult:
    symbol: str
    data: pd.DataFrame
    signals: pd.Series
    trades: list
    equity: pd.Series  # account value at each candle close
    metrics: dict
    final_balance: float  # cash only, open positions aren't counted


class TradingEngine:
    """Connects the data, the strategy, the risk manager, the execution and the portfolio."""

    def __init__(self, data_handler, strategy, risk_manager, execution_manager, portfolio):
        self.data_handler = data_handler
        self.strategy = strategy
        self.risk_manager = risk_manager
        self.execution_manager = execution_manager
        self.portfolio = portfolio

    def process_signal(self, signal: int, symbol: str, price: float, timestamp=None):
        """Makes a trade from a signal if the risk manager agrees. Used by the backtest and the live runner."""
        quantity = self.risk_manager.size_order(
            self.portfolio, signal, price, symbol, fee_rate=self.execution_manager.fee_rate
        )
        if quantity <= 0:
            return None
        return self.execution_manager.execute_trade(
            signal, symbol, quantity, price, self.portfolio, timestamp=timestamp
        )

    def backtest(self, symbol: str, interval: str, start: str, end: str = None) -> BacktestResult:
        data = self.data_handler.get_historical_data(symbol, interval, start, end)
        if data.empty:
            raise ValueError(f"No data for {symbol} {interval} between {start} and {end or 'now'}")
        return self.run_backtest(data, symbol)

    def run_backtest(self, data: pd.DataFrame, symbol: str) -> BacktestResult:
        """
        A candle's signal is only known once the candle has closed, so the trade happens at
        the open of the next one. A signal on the very last candle is never traded.
        """
        logger.info("Backtesting %s over %d candles (%s to %s)", symbol, len(data), data.index[0], data.index[-1])
        signals = self.strategy.generate_signals(data)

        trades = []
        equity = []
        pending_signal = 0
        for timestamp, candle in data.iterrows():
            if pending_signal != 0:
                trade = self.process_signal(pending_signal, symbol, candle["open"], timestamp)
                if trade:
                    trades.append(trade)
            equity.append(self.portfolio.equity({symbol: candle["close"]}))
            pending_signal = signals.loc[timestamp]

        equity = pd.Series(equity, index=data.index, name="equity")
        metrics = summarize(equity, trades, data["close"])
        logger.info("Backtest done. %s", self.portfolio)
        return BacktestResult(symbol, data, signals, trades, equity, metrics, self.portfolio.balance)
