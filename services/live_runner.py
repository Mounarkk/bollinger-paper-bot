# File: services/live_runner.py

import time
import json
import signal
from datetime import datetime
from utils.logger import get_logger

class LiveRunner:
    """
    Runs the trading engine live in paper trading mode.
    """
    def __init__(self, trading_engine, recovery_file="state.json", interval=60):
        """
        Initialize the live runner.

        Parameters:
            trading_engine (TradingEngine): The trading engine instance.
            recovery_file (str): Path to the recovery state file.
            interval (int): Time interval between runs in seconds.
        """
        self.trading_engine = trading_engine
        self.recovery_file = recovery_file
        self.interval = interval
        self.logger = get_logger("LiveRunner")
        self.running = True

        # Load recovery state
        self.recovery_state = self._load_recovery_state()

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._shutdown_handler)
        signal.signal(signal.SIGTERM, self._shutdown_handler)

    def _load_recovery_state(self):
        """
        Load the recovery state from the file.
        """
        try:
            with open(self.recovery_file, "r") as file:
                state = json.load(file)
                self.logger.info(f"Recovery state loaded: {state}")
                return state
        except FileNotFoundError:
            self.logger.warning("No recovery state found, starting fresh.")
            return {}
        except Exception as e:
            self.logger.error(f"Failed to load recovery state: {e}")
            return {}

    def _save_recovery_state(self):
        """
        Save the recovery state to a file.
        """
        state = {
            "portfolio_balance": self.trading_engine.portfolio.balance,
            "positions": self.trading_engine.portfolio.positions,
            "last_run": datetime.utcnow().isoformat()
        }
        try:
            with open(self.recovery_file, "w") as file:
                json.dump(state, file, indent=4)
                self.logger.info("Recovery state saved.")
        except Exception as e:
            self.logger.error(f"Failed to save recovery state: {e}")

    def _shutdown_handler(self, signum, frame):
        """
        Handle shutdown signals for graceful exit.
        """
        self.logger.info("Shutdown signal received. Stopping live runner...")
        self.running = False
        self._save_recovery_state()

    def run(self, symbol, interval):
        """
        Run the live trading loop.
        """
        self.logger.info("Starting live trading...")
        lookback = 20

        while self.running:
            try:
                # Step 1: Fetch live data
                data = self.trading_engine.data_handler.get_recent_klines(symbol, interval, lookback=lookback)

                # Step 2: Generate signals
                signals = self.trading_engine.strategy.generate_signals(data)
                
                # FIX: Only process the most recent signal (the just-closed candle)
                latest_signal = signals.iloc[-1]
                current_price = data['close'].iloc[-1]

                # Step 3: Validate trade
                if self.trading_engine.risk_manager.validate_signal(
                        self.trading_engine.portfolio, latest_signal, current_price, symbol
                ):
                    # Calculate quantity
                    position_size = self.trading_engine.portfolio.balance * self.trading_engine.risk_manager.max_risk_per_trade
                    quantity = position_size / current_price

                    # Step 4: Execute trade
                    self.trading_engine.execution_manager.execute_trade(
                        latest_signal, symbol, quantity, current_price, self.trading_engine.portfolio
                    )

                # Log portfolio state after each loop
                self.logger.info(f"Portfolio state: {self.trading_engine.portfolio}")

                # Step 4: Save recovery state
                self._save_recovery_state()

                # Wait for the next run
                time.sleep(self.interval)

            except Exception as e:
                self.logger.error(f"Error during live run: {e}")
                time.sleep(self.interval)  # Wait before retrying
