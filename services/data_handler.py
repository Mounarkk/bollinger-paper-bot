# File: services/data_handler.py

import pandas as pd
import numpy as np
from binance.client import Client
from datetime import datetime, timedelta

class DataHandler:
    def __init__(self, credentials=None):
        """
        Initialize the DataHandler with optional Binance credentials (see config.load_credentials).
        Without credentials the client can still read public market data, which is all this bot uses.
        """
        api_key = credentials.api_key if credentials else None
        api_secret = credentials.api_secret if credentials else None
        self.client = Client(api_key, api_secret)

    def get_historical_data(self, symbol: str, interval: str, start_date: str, end_date: str = None) -> pd.DataFrame:
        """
        Fetch historical candlestick data for a given symbol and interval.
        """
        print(f"[INFO] Fetching historical data for {symbol}, Interval: {interval}, Start: {start_date}, End: {end_date or 'Now'}")
        klines = self.client.get_historical_klines(
            symbol=symbol,
            interval=interval,
            start_str=start_date,
            end_str=end_date
        )

        # Convert raw data to a pandas DataFrame
        columns = [
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
        ]
        df = pd.DataFrame(klines, columns=columns)

        # Preprocess the DataFrame
        df = self._normalize_historical_data(df)

        return df

    def get_real_time_data(self, symbol: str) -> dict:
        """
        Fetch the latest real-time market data for a given symbol.
        """
        print(f"[INFO] Fetching real-time data for {symbol}")
        ticker = self.client.get_ticker(symbol=symbol)
        data = {
            "symbol": ticker["symbol"],
            "price": float(ticker["lastPrice"]),
            "price_change": float(ticker["priceChangePercent"]),
            "high": float(ticker["highPrice"]),
            "low": float(ticker["lowPrice"]),
            "volume": float(ticker["volume"]),
            "quote_volume": float(ticker["quoteVolume"]),
            "open": float(ticker["openPrice"]),
            "close": float(ticker["lastPrice"]),
            "timestamp": datetime.utcnow()
        }
        return data

    def get_recent_klines(self, symbol: str, interval: str, lookback: int = 20) -> pd.DataFrame:
        """
        Fetch the last `lookback` rows of historical candlestick data for a given symbol and interval.

        Parameters:
            symbol (str): Trading pair (e.g., BTCUSDT).
            interval (str): Kline interval (e.g., 1m, 1h).
            lookback (int): Number of rows to fetch.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the last `lookback` rows.
        """
        print(f"[INFO] Fetching recent data for {symbol}, Interval: {interval}, Lookback window: {lookback}")
        # Fetch historical klines from Binance
        klines = self.client.get_klines(symbol=symbol, interval=interval, limit=lookback)

        # Convert to a pandas DataFrame
        columns = [
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
        ]
        df = pd.DataFrame(klines, columns=columns)

        # Normalize the data
        df = self._normalize_historical_data(df)

        return df


    def _normalize_historical_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize and preprocess the historical candlestick data.
        """
        print(f"[INFO] Normalizing historical data...")

        # Convert timestamp to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")

        # Ensure numeric columns are in proper types
        numeric_columns = ["open", "high", "low", "close", "volume"]
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Set the timestamp as the DataFrame index
        df.set_index("timestamp", inplace=True)

        # Drop unnecessary columns
        df.drop(columns=["close_time", "quote_asset_volume", "number_of_trades", "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"], inplace=True)

        return df

    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate the fetched data for missing or invalid values.
        """
        print(f"[INFO] Validating data...")

        # Check for missing or NaN values
        if df.isnull().values.any():
            print(f"[WARNING] Data contains missing values.")
            return False

        # Check for duplicate timestamps
        if df.index.duplicated().any():
            print(f"[WARNING] Data contains duplicate timestamps.")
            return False

        print(f"[INFO] Data is valid.")
        return True

# Example usage
"""if __name__ == "__main__":
    from config import load_credentials

    data_handler = DataHandler(load_credentials())

    # Fetch historical data
    symbol = "BTCUSDT"
    interval = Client.KLINE_INTERVAL_1HOUR
    start_date = "2023-01-01"

    historical_data = data_handler.get_historical_data(symbol, interval, start_date)
    if data_handler.validate_data(historical_data):
        print(historical_data.head())

    # Fetch real-time data
    real_time_data = data_handler.get_real_time_data(symbol)
    print(real_time_data)"""
