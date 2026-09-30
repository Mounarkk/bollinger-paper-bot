import pandas as pd
import pytest

from services.execution_manager import ExecutionManager
from services.metrics import max_drawdown
from services.portfolio import Portfolio
from services.risk_manager import RiskManager
from services.strategy import Strategy
from services.trading_engine import TradingEngine
from tests.helpers import make_candles


class ScriptedStrategy(Strategy):
    """Returns the signals it was given, so trades can be checked by hand."""
    def __init__(self, signals):
        self.signals = signals

    def generate_signals(self, data):
        return pd.Series(self.signals, index=data.index)


def make_engine(signals, balance=10_000, fee_rate=0.0):
    return TradingEngine(
        data_handler=None,
        strategy=ScriptedStrategy(signals),
        risk_manager=RiskManager(trade_fraction=0.5, min_notional=0),
        execution_manager=ExecutionManager(fee_rate=fee_rate),
        portfolio=Portfolio(balance),
    )


def test_signal_executes_at_next_candle_open():
    data = make_candles(closes=[100, 100, 200, 200], opens=[100, 110, 190, 210])
    result = make_engine([1, 0, -1, 0]).run_backtest(data, "BTCUSDT")

    buy, sell = result.trades
    assert (buy.side, buy.price, buy.timestamp) == ("BUY", 110, data.index[1])
    assert (sell.side, sell.price, sell.timestamp) == ("SELL", 210, data.index[3])


def test_cash_is_counted_once():
    # half of 10 000 buys 50 units at 100, selling them at 200 gives back 10 000
    data = make_candles(closes=[100, 100, 200, 200])
    result = make_engine([1, 0, -1, 0]).run_backtest(data, "BTCUSDT")

    assert result.final_balance == pytest.approx(15_000)
    assert result.trades[1].pnl == pytest.approx(5_000)
    assert result.equity.iloc[-1] == pytest.approx(15_000)
    assert result.metrics["total_return"] == pytest.approx(0.5)
    assert result.metrics["win_rate"] == 1


def test_fees_reduce_the_result():
    data = make_candles(closes=[100, 100, 100, 100])
    result = make_engine([1, 0, -1, 0], fee_rate=0.001).run_backtest(data, "BTCUSDT")
    assert result.final_balance == pytest.approx(10_000 - 5 - 5)
    assert result.metrics["fees_paid"] == pytest.approx(10)
    assert result.metrics["win_rate"] == 0


def test_signal_on_last_candle_is_never_executed():
    data = make_candles(closes=[100, 100, 100])
    result = make_engine([0, 0, 1]).run_backtest(data, "BTCUSDT")
    assert result.trades == []
    assert result.final_balance == 10_000


def test_open_position_counts_in_equity():
    data = make_candles(closes=[100, 100, 50])
    result = make_engine([1, 0, 0]).run_backtest(data, "BTCUSDT")
    assert result.final_balance == pytest.approx(5_000)
    assert result.equity.iloc[-1] == pytest.approx(7_500)
    assert result.metrics["max_drawdown"] == pytest.approx(-0.25)


def test_max_drawdown():
    assert max_drawdown(pd.Series([100, 120, 90, 130, 65])) == pytest.approx(-0.5)
