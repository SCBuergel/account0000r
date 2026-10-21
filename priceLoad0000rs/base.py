"""Base class for price loaders: a USD price for a symbol at a Unix timestamp."""

from abc import ABC, abstractmethod


class basePriceLoad0000r(ABC):
    @abstractmethod
    def name(self):
        """Identifier used in log lines, e.g. "cryptocompare"."""

    @abstractmethod
    def version(self):
        """Version string."""

    @abstractmethod
    def fetchPrice(self, symbol, timestamp):
        """USD price of `symbol` (upper case) at `timestamp`, or None if unknown."""

    def load(self, symbols, timestamp, resolved=None):
        """Price every symbol in `symbols`. Returns (prices, missing): a symbol -> price
        dict and the list of symbols this loader could not price.

        `resolved` holds the prices found by earlier loaders; only the aliases loader
        uses it. Exceptions from fetchPrice are logged and count as missing.
        """
        prices, missing = {}, []
        for symbol in symbols:
            try:
                price = self.fetchPrice(symbol, timestamp)
            except Exception as e:
                print(f"[{self.name()}] error fetching {symbol}: {e}")
                price = None
            if price is None:
                missing.append(symbol)
            else:
                prices[symbol] = price
        return prices, missing
