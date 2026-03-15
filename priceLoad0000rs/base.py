from abc import ABC, abstractmethod
from datetime import datetime


class basePriceLoad0000r(ABC):
    """Abstract base class for EOY (end-of-year) asset price loaders.

    Concrete implementations fetch a closing price in USD for a given symbol
    at a given Unix timestamp.  The orchestrator (loadAssetPrices) calls
    load() on each loader in priority order, stopping at the first success.
    """

    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this price source (e.g. 'cryptocompare')."""
        pass

    @abstractmethod
    def version(self) -> str:
        """Semver-style version string."""
        pass

    @abstractmethod
    def fetchPrice(self, symbol: str, timestamp: int) -> float | None:
        """Return the closing USD price of *symbol* at *timestamp* (Unix seconds).

        Returns None if the price cannot be determined.
        """
        pass

    def load(self, symbols: list[str], timestamp: int) -> tuple[dict, list[str]]:
        """Fetch prices for all *symbols* at *timestamp*.

        Returns
        -------
        prices : dict[str, float]
            Prices that were successfully fetched.
        missing : list[str]
            Symbols for which no price could be found.
        """
        prices = {}
        missing = []
        for symbol in symbols:
            try:
                price = self.fetchPrice(symbol, timestamp)
            except Exception as e:
                print(f"[{self.name()}] error fetching {symbol}: {e}")
                price = None
            if price is not None:
                prices[symbol] = price
            else:
                missing.append(symbol)
        return prices, missing
