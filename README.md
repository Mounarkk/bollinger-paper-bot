# Binance Trading Bot

A modular, event-driven trading engine for Binance, supporting both backtesting and live paper trading.

## Project Structure

The project follows a clean service-oriented architecture:

```
backend/
├── main.py                 # Entry point: Orchestrates the application
├── services/
│   ├── data_handler.py     # Fetches historical and real-time data from Binance
│   ├── strategy.py         # Logic for generating Buy/Sell signals (e.g., Mean Reversion)
│   ├── risk_manager.py     # Validates trades (position sizing, risk limits)
│   ├── execution_manager.py# Handles order execution (Paper or Live)
│   ├── portfolio.py        # Tracks balance and open positions
│   ├── trading_engine.py   # The core loop for Backtesting
│   └── live_runner.py      # The core loop for Live Trading
├── utils/
│   └── logger.py           # Centralized logging
├── .env                    # (Ignored) Stores API keys securely
└── state.json              # (Ignored) Persists state during live runs for recovery
```

## Setup & Configuration

1.  **Environment Variables**:
    Create a `.env` file in the root directory (or export variables in your shell):
    ```bash
    BINANCE_API_KEY="your_api_key"
    BINANCE_API_SECRET="your_api_secret"
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: Ensure `python-dotenv`, `pandas`, `python-binance` are installed)*

## Usage

### Live Trading
Run the bot in live mode (defaults to Paper Trading unless configured otherwise):
```bash
python main.py
```
This will:
1. Load API keys from environment.
2. Initialize the `LiveRunner`.
3. Fetch data every `interval` (e.g., 1 hour).
4. Execute trades and save state to `state.json`.

### Backtesting
To run a backtest, modify `main.py` to use `engine.paper_run()` instead of `LiveRunner`.

## Strategy
The current strategy is **Mean Reversion**:
- Calculates a moving average and standard deviation (Bollinger Bands).
- **Buy**: Price < Lower Band
- **Sell**: Price > Upper Band

## Documentation
This project uses **Sphinx** style docstrings (reStructuredText) for documentation.
