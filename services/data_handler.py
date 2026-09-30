import logging

import pandas as pd
from binance.client import Client

logger = logging.getLogger(__name__)

KLINE_COLUMNS = [
    "timestamp", "open", "high", "low", "close", "volume",
    "close_time", "quote_asset_volume", "number_of_trades",
    "taker_buy_base_volume", "taker_buy_quote_volume", "ignore",
]


class DataHandler:
    def __init__(self, credentials=None, client=None):
        # the tests pass their own fake client so they don't need the network
        if client is None:
            api_key = credentials.api_key if credentials else None
            api_secret = credentials.api_secret if credentials else None
            client = Client(api_key, api_secret)
        self.client = client

    def get_historical_data(self, symbol: str, interval: str, start_date: str, end_date: str = None) -> pd.DataFrame:
        """
        Closed candles between start_date and end_date (now if not given). The dates can be
        anything Binance understands, like "2024-01-01" or "1 month ago UTC".
        """
        logger.info("Fetching %s %s candles from %s to %s", symbol, interval, start_date, end_date or "now")
        klines = self.client.get_historical_klines(
            symbol=symbol,
            interval=interval,
            start_str=start_date,
            end_str=end_date
        )
        return self._normalize(klines)

    def get_recent_klines(self, symbol: str, interval: str, lookback: int = 20) -> pd.DataFrame:
        """The last `lookback` closed candles."""
        # Binance also sends the candle that is still open, _normalize drops it
        klines = self.client.get_klines(symbol=symbol, interval=interval, limit=lookback + 1)
        return self._normalize(klines).tail(lookback)

    @staticmethod
    def _normalize(klines: list) -> pd.DataFrame:
        df = pd.DataFrame(klines, columns=KLINE_COLUMNS)

        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
        numeric_columns = ["open", "high", "low", "close", "volume"]
        df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors="coerce")

        # only keep candles that are finished, their price can't change anymore
        now = pd.Timestamp.now(tz="UTC").tz_localize(None)
        df = df[df["close_time"] < now]

        return df.set_index("timestamp")[numeric_columns]
