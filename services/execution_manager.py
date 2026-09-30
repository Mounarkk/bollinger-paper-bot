import logging
from dataclasses import asdict, dataclass

logger = logging.getLogger(__name__)


@dataclass
class Trade:
    timestamp: object
    symbol: str
    side: str  # "BUY" or "SELL"
    quantity: float
    price: float
    fee: float
    pnl: float | None = None  # only set for sells

    def to_dict(self) -> dict:
        data = asdict(self)
        data["timestamp"] = str(self.timestamp)
        return data


class ExecutionManager:
    """
    Fake order execution. Every order is filled right away at the given price and pays a
    flat fee (0.1% is the default spot fee on Binance). Nothing is ever sent to Binance.
    """
    def __init__(self, fee_rate: float = 0.001):
        self.fee_rate = fee_rate

    def execute_trade(self, signal: int, symbol: str, quantity: float, price: float, portfolio,
                      timestamp=None) -> Trade:
        if signal == 1:
            fee = portfolio.buy(symbol, quantity, price, self.fee_rate)
            trade = Trade(timestamp, symbol, "BUY", quantity, price, fee)
        elif signal == -1:
            fee, pnl = portfolio.sell(symbol, quantity, price, self.fee_rate)
            trade = Trade(timestamp, symbol, "SELL", quantity, price, fee, pnl)
        else:
            raise ValueError(f"Can't execute signal {signal}")

        logger.debug("%s %s %.6f %s at %.2f (fee %.2f)", timestamp, trade.side, quantity, symbol, price, fee)
        return trade
