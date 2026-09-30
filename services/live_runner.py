import json
import logging
import os
import signal
import threading
from datetime import UTC, datetime

import pandas as pd

from services.portfolio import Portfolio

logger = logging.getLogger(__name__)


class LiveRunner:
    """
    Paper trading on live data. Every poll_seconds it checks if a new candle has closed,
    and if so it trades on that candle's signal at its close price. Each candle is only
    traded once. The portfolio is saved to recovery_file after every candle and loaded
    back on start.
    """
    def __init__(self, trading_engine, recovery_file="state.json", poll_seconds=60):
        self.trading_engine = trading_engine
        self.recovery_file = recovery_file
        self.poll_seconds = poll_seconds
        self.last_candle = None
        self._stop = threading.Event()

        self._load_recovery_state()

    def _load_recovery_state(self):
        try:
            with open(self.recovery_file) as file:
                state = json.load(file)
            portfolio = Portfolio.from_dict(state["portfolio"])
        except FileNotFoundError:
            logger.info("No saved state, starting fresh")
            return
        except (OSError, ValueError, KeyError, TypeError) as e:
            raise RuntimeError(f"Could not read {self.recovery_file}, fix or delete it ({e!r})") from e

        self.trading_engine.portfolio = portfolio
        if state.get("last_candle"):
            self.last_candle = pd.Timestamp(state["last_candle"])
        logger.info("Saved state loaded. %s", self.trading_engine.portfolio)

    def _save_recovery_state(self):
        state = {
            "portfolio": self.trading_engine.portfolio.to_dict(),
            "last_candle": self.last_candle.isoformat() if self.last_candle is not None else None,
            "last_run": datetime.now(UTC).isoformat(),
        }
        # write a temp file then rename it, so a crash in the middle can't leave a broken file
        tmp_file = f"{self.recovery_file}.tmp"
        with open(tmp_file, "w") as file:
            json.dump(state, file, indent=4)
        os.replace(tmp_file, self.recovery_file)

    def _shutdown_handler(self, signum, frame):
        logger.info("Stopping...")
        self._stop.set()

    def step(self, symbol: str, interval: str):
        """Trades on the last closed candle if it's a new one. Returns the trade, or None."""
        engine = self.trading_engine
        data = engine.data_handler.get_recent_klines(symbol, interval, lookback=engine.strategy.lookback)
        if data.empty:
            return None

        candle_time = data.index[-1]
        if self.last_candle is not None and candle_time <= self.last_candle:
            return None  # same candle as last time

        latest_signal = int(engine.strategy.generate_signals(data).iloc[-1])
        price = data["close"].iloc[-1]
        trade = engine.process_signal(latest_signal, symbol, price, candle_time)

        self.last_candle = candle_time
        if trade:
            logger.info("%s %.6f %s at %.2f (fee %.2f)", trade.side, trade.quantity, symbol, price, trade.fee)
        logger.info("Candle %s UTC closed at %.2f, signal %d. %s", candle_time, price, latest_signal, engine.portfolio)
        self._save_recovery_state()
        return trade

    def run(self, symbol: str, interval: str):
        logger.info("Starting live paper trading on %s %s", symbol, interval)
        signal.signal(signal.SIGINT, self._shutdown_handler)
        signal.signal(signal.SIGTERM, self._shutdown_handler)
        try:
            while not self._stop.is_set():
                try:
                    self.step(symbol, interval)
                except Exception:
                    # a network error shouldn't kill the loop, it just tries again next time
                    logger.exception("Error during live run, retrying in %ss", self.poll_seconds)
                self._stop.wait(self.poll_seconds)
        finally:
            self._save_recovery_state()
            logger.info("Stopped. %s", self.trading_engine.portfolio)
