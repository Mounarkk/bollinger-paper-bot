# File: main.py

from services.data_handler import DataHandler
from services.strategy import MeanReversionStrategy
from services.risk_manager import RiskManager
from services.execution_manager import ExecutionManager
from services.portfolio import Portfolio
from services.trading_engine import TradingEngine
from services.live_runner import LiveRunner
from config import load_credentials

# Credentials come from the environment (or a git-ignored `.env`), never from code.
# They are optional: only public market-data endpoints are used.
credentials = load_credentials()
if not credentials.is_set:
    print("[INFO] No Binance API keys set, using public market data only.")

# FOR BACK-TESTS
"""
if __name__ == "__main__":
    # Initialize components
    data_handler = DataHandler(credentials)
    strategy = MeanReversionStrategy()
    risk_manager = RiskManager()
    execution_manager = ExecutionManager()
    portfolio = Portfolio()

    # Initialize engine
    engine = TradingEngine(data_handler, strategy, risk_manager, execution_manager, portfolio)

    # Run engine in paper trading mode
    engine.run("FETUSDT", "2h")
"""

# FOR LIVE RUN
if __name__ == "__main__":
    # Initialize components
    data_handler = DataHandler(credentials)
    strategy = MeanReversionStrategy()
    risk_manager = RiskManager()
    execution_manager = ExecutionManager()
    portfolio = Portfolio(initial_balance=10000)

    # Initialize trading engine
    engine = TradingEngine(data_handler, strategy, risk_manager, execution_manager, portfolio)

    # Initialize live runner
    live_runner = LiveRunner(trading_engine=engine, interval=60, recovery_file="./state.json")

    # Start live trading
    live_runner.run(symbol="BTCUSDT", interval="1h")
