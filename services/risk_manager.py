class RiskManager:
    """
    Decides how much to trade on each signal. It's very basic, there's no stop loss or anything like it.

    A buy spends a fixed part of the cash, so several buy signals in a row keep adding to
    the position. A sell closes everything. Orders worth less than min_notional are
    skipped, Binance would refuse them anyway.
    """

    def __init__(self, trade_fraction: float = 0.02, min_notional: float = 10.0):
        self.trade_fraction = trade_fraction
        self.min_notional = min_notional

    def size_order(self, portfolio, signal: int, price: float, symbol: str, fee_rate: float = 0.0) -> float:
        """Quantity to trade, or 0 to skip the signal."""
        if price <= 0:
            return 0.0

        if signal == 1:
            quantity = portfolio.balance * self.trade_fraction / price
            if quantity * price < self.min_notional:
                return 0.0
            if quantity * price * (1 + fee_rate) > portfolio.balance:
                return 0.0
            return quantity

        if signal == -1:
            quantity = portfolio.get_position_quantity(symbol)
            if quantity * price < self.min_notional:
                return 0.0
            return quantity

        return 0.0
