# File: services/portfolio.py

class Portfolio:
    """
    Tracks portfolio state, including balances and positions.
    """
    def __init__(self, initial_balance: float = 1000):
        self.balance = initial_balance
        self.positions = {}  # {symbol: {'quantity': float, 'average_price': float}}

    def update_position(self, symbol: str, signal: int, quantity: float, price: float):
        """
        Update the position for the given symbol.

        Parameters:
            symbol (str): Trading pair (e.g., BTCUSDT).
            signal (int): 1 for BUY, -1 for SELL.
            quantity (float): Quantity of the asset traded.
            price (float): Trade price.
        """
        if signal == 1:  # BUY
            if symbol in self.positions:
                # Update the existing position
                old_quantity = self.positions[symbol]['quantity']
                old_avg_price = self.positions[symbol]['average_price']
                new_quantity = old_quantity + quantity
                new_avg_price = ((old_avg_price * old_quantity) + (price * quantity)) / new_quantity
                self.positions[symbol] = {'quantity': new_quantity, 'average_price': new_avg_price}
            else:
                # New position
                self.positions[symbol] = {'quantity': quantity, 'average_price': price}
            self.balance -= quantity * price  # Deduct cost

        elif signal == -1:  # SELL
            if symbol in self.positions and self.positions[symbol]['quantity'] >= quantity:
                self.positions[symbol]['quantity'] -= quantity
                self.balance += quantity * price  # Add proceeds
                if self.positions[symbol]['quantity'] == 0:
                    del self.positions[symbol]  # Close the position if fully sold

    def get_position_quantity(self, symbol: str) -> float:
        """
        Get the quantity of the open position for a symbol.

        Parameters:
            symbol (str): Trading pair.

        Returns:
            float: Quantity of the open position. Defaults to 0.
        """
        return self.positions.get(symbol, {}).get('quantity', 0)

    def __str__(self):
        return f"Portfolio Balance: ${self.balance:.2f}, Positions: {self.positions}"
