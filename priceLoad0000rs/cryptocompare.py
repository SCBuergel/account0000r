import time
import requests
from priceLoad0000rs.base import basePriceLoad0000r


_BASE_URL = "https://min-api.cryptocompare.com/data/v2/histoday"
_RATE_LIMIT_MSG = "you are over your rate limit"


class load0000r(basePriceLoad0000r):
    """Fetch EOY prices from the CryptoCompare histoday API.

    Permissionless — no API key required.  Returns the *close* of the daily
    candle whose timestamp equals *toTs* (i.e. midnight UTC of the target day).

    The API returns two candles for limit=1: the candle *before* toTs and the
    candle *at* toTs.  We take the last entry so the returned price is the
    close of the day that ends at toTs.

    Example:
        toTs = 1735689600  # 2025-01-01 00:00:00 UTC  →  EOY 2024 close
    """

    def name(self) -> str:
        return "cryptocompare"

    def version(self) -> str:
        return "0.0.1"

    def fetchPrice(self, symbol: str, timestamp: int) -> float | None:
        params = {
            "fsym": symbol.upper(),
            "tsym": "USD",
            "limit": 1,
            "toTs": timestamp,
        }

        attempt = 0
        wait_time = 1
        max_attempts = 10
        max_wait = 60

        while True:
            response = requests.get(_BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("Response") == "Success":
                break

            message = data.get("Message", "")
            if _RATE_LIMIT_MSG in message.lower():
                attempt += 1
                if attempt > max_attempts:
                    print(f"[cryptocompare] rate limit exceeded after {max_attempts} retries for {symbol}, giving up")
                    return None
                print(f"[cryptocompare] rate limited for {symbol}, retrying in {wait_time}s (attempt {attempt}/{max_attempts})")
                time.sleep(wait_time)
                wait_time = min(2 ** attempt, max_wait)
            else:
                print(f"[cryptocompare] non-success response for {symbol}: {message}")
                return None

        candles = data.get("Data", {}).get("Data", [])
        if not candles:
            return None

        # The last candle is the one closing at toTs
        close = candles[-1].get("close")
        if close == 0:
            # CryptoCompare returns 0 when it has no data for the symbol
            return None
        return close
