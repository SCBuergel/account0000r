from priceLoad0000rs.base import basePriceLoad0000r


class load0000r(basePriceLoad0000r):
    """Price derived/wrapped/staked tokens at the same price as their underlying asset.

    This loader should be placed *last* in the loaders list so that the
    underlying prices have already been resolved by earlier loaders.

    Parameters
    ----------
    mapping : dict[str, str]
        Maps derived token symbol to underlying symbol (case-insensitive).

    Example::

        from priceLoad0000rs.aliases import load0000r as Aliases

        aliases = Aliases({
            "XHOPR":   "HOPR",
            "WXHOPR":  "HOPR",
            "STKAAVE": "AAVE",
            "WETH":    "ETH",
            "STETH":   "ETH",
            "WBTC":    "BTC",
            "USDC.E":  "USDC",
        })
    """

    def __init__(self, mapping: dict[str, str]):
        self._mapping = {k.upper(): v.upper() for k, v in mapping.items()}

    def name(self) -> str:
        return "aliases"

    def version(self) -> str:
        return "0.0.1"

    def fetchPrice(self, symbol: str, timestamp: int) -> float | None:
        # fetchPrice has no access to already-resolved prices; use load() instead.
        return None

    def load(self, symbols: list[str], timestamp: int, resolved: dict | None = None) -> tuple[dict, list[str]]:
        resolved = resolved or {}
        prices = {}
        missing = []
        for symbol in symbols:
            underlying = self._mapping.get(symbol.upper())
            if underlying is None:
                missing.append(symbol)
                continue
            price = resolved.get(underlying)
            if price is not None:
                print(f"[aliases] {symbol} → {underlying} @ ${price:,.4f}")
                prices[symbol] = price
            else:
                print(f"[aliases] {symbol} → {underlying} but {underlying} has no price yet — load {underlying} first")
                missing.append(symbol)
        return prices, missing
