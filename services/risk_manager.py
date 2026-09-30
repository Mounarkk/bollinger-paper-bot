# File: services/risk_manager.py

class RiskManager:
    """
    Validates trade signals based on risk management rules.
    """

    def __init__(self, max_risk_per_trade: float = 0.02, min_trade_size: float = 0.001):
        self.max_risk_per_trade = max_risk_per_trade
        self.min_trade_size = min_trade_size

    def validate_signal(self, portfolio, signal: int, price: float, symbol: str) -> bool:
        """
        Validate whether a trade signal adheres to risk management rules.

        Parameters:
            portfolio (Portfolio): The portfolio object to check positions.
            signal (int): Trade signal (1 for BUY, -1 for SELL).
            price (float): Current asset price.
            symbol (str): Trading pair.

        Returns:
            bool: True if the trade is valid, False otherwise.
        """
        position_size = portfolio.balance * self.max_risk_per_trade
        quantity = position_size / price if price > 0 else 0

        if signal == 1:  # BUY
            if quantity < self.min_trade_size:
                print(f"[WARNING] Trade size ({quantity:.6f}) is below the minimum trade size.")
                return False
            return True

        elif signal == -1:  # SELL
            open_quantity = portfolio.get_position_quantity(symbol)
            if open_quantity == 0:
                print(f"[WARNING] No open position to SELL for {symbol}.")
                return False
            return True

