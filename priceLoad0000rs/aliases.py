"""Price wrapped, staked or bridged tokens at the price of their underlying asset.

Place this loader after the loaders that price the underlying assets.
"""

from priceLoad0000rs.base import basePriceLoad0000r

DEFAULT_ALIASES = {
    "XHOPR": "HOPR", "WXHOPR": "HOPR",
    "STKAAVE": "AAVE",
    "STETH": "ETH", "WETH": "ETH",
    "WBTC": "BTC",
    "XDAI": "DAI",
    "USDC.E": "USDC",
}


class load0000r(basePriceLoad0000r):
    def __init__(self, mapping=None):
        mapping = DEFAULT_ALIASES if mapping is None else mapping
        self._mapping = {k.upper(): v.upper() for k, v in mapping.items()}

    def name(self):
        return "aliases"

    def version(self):
        return "0.0.1"

    def fetchPrice(self, symbol, timestamp):
        return None  # needs the already resolved prices, so load() is overridden instead

    def load(self, symbols, timestamp, resolved=None):
        resolved = resolved or {}
        prices, missing = {}, []
        for symbol in symbols:
            underlying = self._mapping.get(symbol.upper())
            price = resolved.get(underlying) if underlying else None
            if price is None:
                if underlying:
                    print(f"[aliases] {symbol} -> {underlying}, but {underlying} has no price yet")
                missing.append(symbol)
            else:
                print(f"[aliases] {symbol} -> {underlying} @ ${price:,.4f}")
                prices[symbol] = price
        return prices, missing
