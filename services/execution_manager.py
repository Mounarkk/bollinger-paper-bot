# File: services/execution_manager.py

class ExecutionManager:
    """
    Handles simulated order placement.
    """
    def __init__(self, mode: str = "paper"):
        self.mode = mode  # "paper" for simulation, "live" for real trading

    def execute_trade(self, signal: int, symbol: str, quantity: float, price: float, portfolio):
        """
        Execute a trade based on the provided signal.

        Parameters:
            signal (int): 1 for BUY, -1 for SELL.
            symbol (str): Trading pair (e.g., BTCUSDT).
            quantity (float): Quantity of the asset to trade.
            price (float): Price of the asset.
            portfolio (Portfolio): The portfolio to update.
        """
        if signal == 1:  # BUY
            print(f"[EXECUTION] BUY {quantity:.6f} {symbol} at {price:.2f}")
        elif signal == -1:  # SELL
            print(f"[EXECUTION] SELL {quantity:.6f} {symbol} at {price:.2f}")
        else:
            print("[EXECUTION] HOLD - No trade executed.")

        # Update portfolio
        portfolio.update_position(symbol, signal, quantity, price)
