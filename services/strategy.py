# File: services/strategy.py

import pandas as pd

class Strategy:
    """
    Base class for trading strategies.
    """
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        raise NotImplementedError("Subclasses must implement this method.")


class MeanReversionStrategy(Strategy):
    """
    Implements a mean reversion trading strategy.
    """
    def __init__(self, lookback: int = 20, threshold: float = 1.5):
        self.lookback = lookback
        self.threshold = threshold

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trade signals based on mean reversion logic.
        """
        # Calculate moving average and standard deviation
        data['mean'] = data['close'].rolling(window=self.lookback).mean()
        data['std'] = data['close'].rolling(window=self.lookback).std()

        # Calculate upper and lower bands
        data['upper_band'] = data['mean'] + (self.threshold * data['std'])
        data['lower_band'] = data['mean'] - (self.threshold * data['std'])

        # Generate signals
        data['signal'] = 0  # Default to HOLD
        data.loc[data['close'] > data['upper_band'], 'signal'] = -1  # SELL
        data.loc[data['close'] < data['lower_band'], 'signal'] = 1   # BUY

        return data['signal']
