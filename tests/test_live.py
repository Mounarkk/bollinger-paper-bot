import json

import pandas as pd
import pytest

from services.data_handler import DataHandler
from services.execution_manager import ExecutionManager
from services.live_runner import LiveRunner
from services.portfolio import Portfolio
from services.risk_manager import RiskManager
from services.strategy import MeanReversionStrategy
from services.trading_engine import TradingEngine

HOUR_MS = 3_600_000


class FakeClient:
    """Fake Client.get_klines with hourly candles. Like the real one, the last candle is still open."""
    def __init__(self, closes):
        self.closes = closes

    def get_klines(self, symbol, interval, limit):
        now_ms = int(pd.Timestamp.now(tz="UTC").timestamp() * 1000)
        forming_open = now_ms - now_ms % HOUR_MS
        closes = self.closes[-(limit - 1):] + [999_999]  # the open candle gets a silly price
        first_open = forming_open - (len(closes) - 1) * HOUR_MS
        return [
            [first_open + i * HOUR_MS, str(c), str(c), str(c), str(c), "1.0",
             first_open + (i + 1) * HOUR_MS - 1, "0", 0, "0", "0", "0"]
            for i, c in enumerate(closes)
        ]


def test_recent_klines_drop_the_forming_candle():
    data = DataHandler(client=FakeClient([100.0] * 30)).get_recent_klines("BTCUSDT", "1h", lookback=20)
    assert len(data) == 20
    assert list(data.columns) == ["open", "high", "low", "close", "volume"]
    assert data["close"].max() == 100.0
    assert data.index[-1] < pd.Timestamp.now(tz="UTC").tz_localize(None)


def make_runner(closes, state_file, balance=10_000):
    engine = TradingEngine(
        data_handler=DataHandler(client=FakeClient(closes)),
        strategy=MeanReversionStrategy(lookback=20, threshold=1.5),
        risk_manager=RiskManager(),
        execution_manager=ExecutionManager(),
        portfolio=Portfolio(balance),
    )
    return LiveRunner(engine, recovery_file=str(state_file), poll_seconds=0)


def test_each_candle_is_traded_once(tmp_path):
    runner = make_runner([100, 101] * 15 + [80], tmp_path / "state.json")

    trade = runner.step("BTCUSDT", "1h")
    assert trade.side == "BUY" and trade.price == 80

    assert runner.step("BTCUSDT", "1h") is None  # same candle, polled again
    assert len(runner.trading_engine.portfolio.positions) == 1


def test_state_is_saved_and_restored(tmp_path):
    state_file = tmp_path / "state.json"
    runner = make_runner([100, 101] * 15 + [80], state_file)
    runner.step("BTCUSDT", "1h")
    saved_balance = runner.trading_engine.portfolio.balance

    state = json.loads(state_file.read_text())
    assert state["portfolio"]["balance"] == pytest.approx(saved_balance)
    assert "BTCUSDT" in state["portfolio"]["positions"]

    restarted = make_runner([100, 101] * 15 + [80], state_file, balance=1)
    assert restarted.trading_engine.portfolio.balance == pytest.approx(saved_balance)
    assert restarted.step("BTCUSDT", "1h") is None  # already traded before the restart


def test_unreadable_state_fails_loudly(tmp_path):
    state_file = tmp_path / "state.json"
    state_file.write_text('{"portfolio_balance": 5000}')  # old 2024 format
    with pytest.raises(RuntimeError):
        make_runner([100] * 30, state_file)
