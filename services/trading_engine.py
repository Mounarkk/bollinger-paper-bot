# File: services/trading_engine.py

class TradingEngine:
    """
    Orchestrates the trading workflow.
    """
    def __init__(self, data_handler, strategy, risk_manager, execution_manager, portfolio):
        self.data_handler = data_handler
        self.strategy = strategy
        self.risk_manager = risk_manager
        self.execution_manager = execution_manager
        self.portfolio = portfolio

    def paper_run(self, symbol: str, interval: str):
        """
        Run the trading workflow.
        """
        print(f"[INFO] Starting trading engine for {symbol}, Interval: {interval}")

        # Step 1: Fetch historical or real-time data
        data = self.data_handler.get_historical_data(symbol, interval, "2024-11-01")

        # Step 2: Generate signals
        signals = self.strategy.generate_signals(data)

        # FIX: Iterate up to len(signals) - 1 because we execute on the NEXT candle
        for i in range(len(signals) - 1):
            signal = signals.iloc[i]
            
            # We execute at the OPEN price of the NEXT candle (i+1)
            # This simulates reality: you get the signal at Close of i, and buy at Open of i+1
            execution_price = data['open'].iloc[i + 1]

            # Step 3: Validate trade using Risk Manager
            position_size = self.portfolio.balance * self.risk_manager.max_risk_per_trade
            quantity = position_size / execution_price if execution_price > 0 else 0

            is_valid_trade = self.risk_manager.validate_signal(
                portfolio=self.portfolio,
                signal=signal,
                price=execution_price,
                symbol=symbol
            )

            if is_valid_trade:
                # Step 4: Execute trade
                self.execution_manager.execute_trade(
                    signal=signal,
                    symbol=symbol,
                    quantity=quantity,
                    price=execution_price,
                    portfolio=self.portfolio
                )

                # Step 5: Update Portfolio
                trade_value = quantity * execution_price
                self.portfolio.balance += (-trade_value if signal == 1 else trade_value)

        print(f"[INFO] Trading session complete. Portfolio: {self.portfolio}")
