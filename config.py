import os
from dataclasses import dataclass, field

try:
    # lets you keep the keys in a local .env file, which git ignores
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass(frozen=True)
class BinanceCredentials:
    """API keys from the environment. The bot works without them since it only reads public data."""
    api_key: str | None = field(default=None, repr=False)
    api_secret: str | None = field(default=None, repr=False)

    @property
    def is_set(self) -> bool:
        return bool(self.api_key and self.api_secret)

    def __repr__(self):
        # never show the keys, even in a traceback
        return f"BinanceCredentials(is_set={self.is_set})"


def load_credentials() -> BinanceCredentials:
    return BinanceCredentials(
        api_key=os.getenv("BINANCE_API_KEY") or None,
        api_secret=os.getenv("BINANCE_API_SECRET") or None,
    )
