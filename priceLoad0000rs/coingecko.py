"""Historical prices from the CoinGecko /coins/{id}/history endpoint.

Without a key the public API serves dates within the last 365 days only, which is enough
for current prices and for an end-of-year run done early in the next year. A demo key in
the COINGECKO_API_KEY environment variable lifts the rate limit but not the 365-day limit.

CoinGecko identifies coins by id ("ethereum"), not symbol. The full coin list is
downloaded once to map symbol -> id; where several coins share a symbol the first match
wins unless DEFAULT_IDS or symbol_overrides pins the id.
"""

import os
from datetime import datetime, timezone

import requests

from priceLoad0000rs.base import basePriceLoad0000r

_COINS_LIST_URL = "https://api.coingecko.com/api/v3/coins/list"
_HISTORY_URL = "https://api.coingecko.com/api/v3/coins/{id}/history"

DEFAULT_IDS = {
    "ETH": "ethereum", "WETH": "weth", "USDC": "usd-coin", "USDT": "tether", "DAI": "dai",
    "WBTC": "wrapped-bitcoin", "XDAI": "xdai", "GNO": "gnosis", "MATIC": "matic-network",
    "BNB": "binancecoin", "COW": "cow-protocol",
}


def _get(url, params):
    """GET a CoinGecko URL and return its JSON. Raises with the API's own message on errors."""
    headers = {}
    if os.environ.get("COINGECKO_API_KEY"):
        headers["x-cg-demo-api-key"] = os.environ["COINGECKO_API_KEY"]
    response = requests.get(url, params=params, headers=headers, timeout=15)
    data = response.json()
    if response.status_code != 200:
        error = data.get("error", data) if isinstance(data, dict) else data
        if isinstance(error, dict):  # {"error": {"status": {"error_message": ...}}}
            error = error.get("status", {}).get("error_message", error)
        raise RuntimeError(f"HTTP {response.status_code}: {error}")
    return data


class load0000r(basePriceLoad0000r):
    def __init__(self, symbol_overrides=None):
        self._ids = {**DEFAULT_IDS, **{k.upper(): v for k, v in (symbol_overrides or {}).items()}}
        self._listFetched = False

    def name(self):
        return "coingecko"

    def version(self):
        return "0.0.2"

    def _resolveIds(self, symbols):
        """Add ids for `symbols` not yet known, downloading the coin list once."""
        wanted = {s.upper() for s in symbols} - set(self._ids)
        if not wanted or self._listFetched:
            return
        print("[coingecko] fetching the coin list to map symbols to ids")
        coins = _get(_COINS_LIST_URL, {"include_platform": "false"})
        self._listFetched = True
        for coin in coins:
            sym = coin["symbol"].upper()
            if sym in wanted and sym not in self._ids:
                self._ids[sym] = coin["id"]

    def fetchPrice(self, symbol, timestamp):
        sym = symbol.upper()
        self._resolveIds([sym])
        coinId = self._ids.get(sym)
        if coinId is None:
            print(f"[coingecko] no coin id for {sym}")
            return None
        date = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%d-%m-%Y")
        data = _get(_HISTORY_URL.format(id=coinId), {"date": date, "localization": "false"})
        try:
            return data["market_data"]["current_price"]["usd"]
        except (KeyError, TypeError):
            print(f"[coingecko] no price for {sym} ({coinId}) on {date}")
            return None

    def load(self, symbols, timestamp, resolved=None):
        self._resolveIds(symbols)  # one list download for all symbols
        return super().load(symbols, timestamp)
