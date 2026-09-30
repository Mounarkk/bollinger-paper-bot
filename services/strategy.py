import pandas as pd


class Strategy:
    """Base class. generate_signals returns 1 (buy), -1 (sell) or 0 (hold) for each candle."""
    lookback = 1

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        raise NotImplementedError


class MeanReversionStrategy(Strategy):
    """
    Bollinger bands. Buys when the close goes under the lower band and sells when it
    goes over the upper one, hoping the price comes back to its average.
    """
    def __init__(self, lookback: int = 20, threshold: float = 1.5):
        self.lookback = lookback
        self.threshold = threshold

    def compute_bands(self, data: pd.DataFrame) -> pd.DataFrame:
        mean = data["close"].rolling(window=self.lookback).mean()
        std = data["close"].rolling(window=self.lookback).std()
        return pd.DataFrame({
            "mean": mean,
            "upper_band": mean + self.threshold * std,
            "lower_band": mean - self.threshold * std,
        }, index=data.index)

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        bands = self.compute_bands(data)

        signals = pd.Series(0, index=data.index, name="signal")
        signals[data["close"] > bands["upper_band"]] = -1
        signals[data["close"] < bands["lower_band"]] = 1
        return signals
