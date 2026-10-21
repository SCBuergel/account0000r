"""Daily close prices from the CryptoCompare (now CoinDesk) histoday API.

The API needs a key since 2025: put it in the CRYPTOCOMPARE_API_KEY environment variable
(free keys at https://developers.coindesk.com/). Without a key the loader prices nothing.

With limit=1 the API returns the candle before `toTs` and the candle at `toTs`; the
last one is the close of the day ending at `toTs`, e.g. toTs=1735689600 (2025-01-01
00:00 UTC) gives the end-of-2024 price.
"""

import os
import time

import requests

from priceLoad0000rs.base import basePriceLoad0000r

_BASE_URL = "https://min-api.cryptocompare.com/data/v2/histoday"
_RATE_LIMIT_MSG = "rate limit"


class load0000r(basePriceLoad0000r):
    def __init__(self, api_key=None):
        self._api_key = api_key or os.environ.get("CRYPTOCOMPARE_API_KEY")

    def name(self):
        return "cryptocompare"

    def version(self):
        return "0.0.2"

    def load(self, symbols, timestamp, resolved=None):
        if not self._api_key:
            print("[cryptocompare] skipped: set CRYPTOCOMPARE_API_KEY to use this source")
            return {}, list(symbols)
        return super().load(symbols, timestamp, resolved)

    def fetchPrice(self, symbol, timestamp, max_attempts=10, max_wait=60):
        params = {"fsym": symbol.upper(), "tsym": "USD", "limit": 1, "toTs": timestamp}
        headers = {"authorization": f"Apikey {self._api_key}"}
        for attempt in range(1, max_attempts + 1):
            data = requests.get(_BASE_URL, params=params, headers=headers, timeout=10).json()
            if data.get("Response") == "Success":
                break
            message = data.get("Message") or data.get("Err", {}).get("message", "unknown error")
            if _RATE_LIMIT_MSG not in message.lower():
                print(f"[cryptocompare] no price for {symbol}: {message}")
                return None
            if attempt == max_attempts:
                print(f"[cryptocompare] still rate limited after {max_attempts} attempts for {symbol}")
                return None
            wait = min(2 ** attempt, max_wait)
            print(f"[cryptocompare] rate limited for {symbol}, retrying in {wait}s ({attempt}/{max_attempts})")
            time.sleep(wait)
        candles = data.get("Data", {}).get("Data", [])
        close = candles[-1].get("close") if candles else None
        return close or None  # 0 means CryptoCompare has no data for the symbol
