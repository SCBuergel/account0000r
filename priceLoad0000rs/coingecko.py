import requests
from datetime import datetime, timezone
from priceLoad0000rs.base import basePriceLoad0000r


_COINS_LIST_URL = "https://api.coingecko.com/api/v3/coins/list"
_HISTORY_URL = "https://api.coingecko.com/api/v3/coins/{id}/history"


class load0000r(basePriceLoad0000r):
    """Fetch EOY prices from the CoinGecko /coins/{id}/history endpoint.

    CoinGecko identifies assets by *id* (e.g. "ethereum"), not by ticker
    symbol.  On first use this loader downloads the full coin list and builds
    a symbol→id mapping.  When multiple coins share the same symbol the user
    can pass *symbol_overrides* to pin specific CoinGecko ids.

    Parameters
    ----------
    symbol_overrides : dict[str, str], optional
        Maps uppercase ticker symbol to the preferred CoinGecko coin id.
        Example: {"ETH": "ethereum", "USDC": "usd-coin"}
    """

    def __init__(self, symbol_overrides: dict | None = None):
        self._symbol_overrides = {k.upper(): v for k, v in (symbol_overrides or {}).items()}
        self._id_map: dict[str, str] = {}   # populated lazily

    def name(self) -> str:
        return "coingecko"

    def version(self) -> str:
        return "0.0.1"

    def _ensure_id_map(self, symbols: list[str]) -> None:
        """Populate self._id_map for all *symbols* not already resolved."""
        unresolved = [s for s in symbols if s.upper() not in self._id_map and s.upper() not in self._symbol_overrides]
        if not unresolved:
            return

        print("[coingecko] fetching coin list to resolve symbol→id mapping…")
        response = requests.get(_COINS_LIST_URL, params={"include_platform": "false"}, timeout=15)
        response.raise_for_status()
        coin_list = response.json()

        upper_unresolved = {s.upper() for s in unresolved}
        for coin in coin_list:
            sym = coin["symbol"].upper()
            if sym in upper_unresolved and sym not in self._id_map:
                # Keep first match; user can override ambiguous ones via symbol_overrides
                self._id_map[sym] = coin["id"]

    def fetchPrice(self, symbol: str, timestamp: int) -> float | None:
        sym = symbol.upper()

        # Resolve CoinGecko id
        coin_id = self._symbol_overrides.get(sym) or self._id_map.get(sym)
        if coin_id is None:
            # Lazy single-symbol resolution
            self._ensure_id_map([sym])
            coin_id = self._symbol_overrides.get(sym) or self._id_map.get(sym)
        if coin_id is None:
            print(f"[coingecko] no coin id found for {sym}")
            return None

        # CoinGecko /history expects DD-MM-YYYY
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        date_str = dt.strftime("%d-%m-%Y")

        response = requests.get(
            _HISTORY_URL.format(id=coin_id),
            params={"date": date_str, "localization": "false"},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        try:
            price = data["market_data"]["current_price"]["usd"]
        except (KeyError, TypeError):
            print(f"[coingecko] no price in response for {sym} ({coin_id}) on {date_str}")
            return None
        return price

    def load(self, symbols: list[str], timestamp: int, resolved: dict | None = None) -> tuple[dict, list[str]]:
        """Override to pre-resolve the full symbol list in one API call."""
        self._ensure_id_map(symbols)
        return super().load(symbols, timestamp)
