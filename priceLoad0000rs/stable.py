"""Stablecoins pegged to the US dollar are priced at exactly 1 USD.

Pegs do wobble by a fraction of a percent; for the portfolio total that is noise, and
the APIs often fail to price bridged variants (USDC.E) at all.
"""

from priceLoad0000rs.base import basePriceLoad0000r

STABLECOINS = {"DAI", "USDC", "USDC.E", "USDT", "XDAI"}


class load0000r(basePriceLoad0000r):
    def __init__(self, symbols=STABLECOINS):
        self._symbols = {s.upper() for s in symbols}

    def name(self):
        return "stablecoins"

    def version(self):
        return "0.0.1"

    def fetchPrice(self, symbol, timestamp):
        return 1.0 if symbol.upper() in self._symbols else None
