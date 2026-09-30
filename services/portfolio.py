# anything smaller is float noise, the position counts as closed
DUST = 1e-12


class Portfolio:
    """
    Cash and open positions of the simulated account.
    average_price includes the fees paid when buying.
    """
    def __init__(self, initial_balance: float = 1000):
        self.initial_balance = float(initial_balance)
        self.balance = float(initial_balance)
        self.positions = {}  # symbol -> {"quantity", "average_price"}

    def buy(self, symbol: str, quantity: float, price: float, fee_rate: float = 0.0) -> float:
        """Returns the fee paid."""
        quantity, price = float(quantity), float(price)
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        fee = quantity * price * fee_rate
        cost = quantity * price + fee
        if cost > self.balance:
            raise ValueError(f"Not enough cash, need {cost:.2f} and have {self.balance:.2f}")

        position = self.positions.get(symbol, {"quantity": 0.0, "average_price": 0.0})
        new_quantity = position["quantity"] + quantity
        new_average = (position["quantity"] * position["average_price"] + cost) / new_quantity
        self.positions[symbol] = {"quantity": new_quantity, "average_price": new_average}
        self.balance -= cost
        return fee

    def sell(self, symbol: str, quantity: float, price: float, fee_rate: float = 0.0) -> tuple[float, float]:
        """Returns the fee paid and the profit made on this sale."""
        quantity, price = float(quantity), float(price)
        held = self.get_position_quantity(symbol)
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if quantity > held + DUST:
            raise ValueError(f"Can't sell {quantity} {symbol}, only {held} held")

        fee = quantity * price * fee_rate
        proceeds = quantity * price - fee
        pnl = proceeds - quantity * self.positions[symbol]["average_price"]

        self.balance += proceeds
        self.positions[symbol]["quantity"] -= quantity
        if self.positions[symbol]["quantity"] <= DUST:
            del self.positions[symbol]
        return fee, pnl

    def get_position_quantity(self, symbol: str) -> float:
        return self.positions.get(symbol, {}).get("quantity", 0.0)

    def equity(self, prices: dict) -> float:
        """Cash plus the value of the positions at the given prices."""
        return self.balance + sum(
            position["quantity"] * prices[symbol] for symbol, position in self.positions.items()
        )

    def to_dict(self) -> dict:
        return {
            "initial_balance": self.initial_balance,
            "balance": float(self.balance),
            "positions": {
                symbol: {"quantity": float(p["quantity"]), "average_price": float(p["average_price"])}
                for symbol, p in self.positions.items()
            },
        }

    @classmethod
    def from_dict(cls, state: dict) -> "Portfolio":
        portfolio = cls(state.get("initial_balance", state["balance"]))
        portfolio.balance = float(state["balance"])
        portfolio.positions = {
            symbol: {"quantity": float(p["quantity"]), "average_price": float(p["average_price"])}
            for symbol, p in state.get("positions", {}).items()
        }
        return portfolio

    def __str__(self):
        return f"Portfolio Balance: ${self.balance:.2f}, Positions: {self.positions}"
