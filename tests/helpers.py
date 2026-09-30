import pandas as pd


def make_candles(closes, opens=None, start="2024-01-01", freq="1h"):
    """Build a candle DataFrame shaped like DataHandler's output."""
    opens = closes if opens is None else opens
    index = pd.date_range(start, periods=len(closes), freq=freq, name="timestamp")
    return pd.DataFrame({
        "open": [float(o) for o in opens],
        "high": [max(o, c) * 1.01 for o, c in zip(opens, closes, strict=True)],
        "low": [min(o, c) * 0.99 for o, c in zip(opens, closes, strict=True)],
        "close": [float(c) for c in closes],
        "volume": 1.0,
    }, index=index)
