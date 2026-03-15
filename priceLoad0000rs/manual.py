import csv
import os
from priceLoad0000rs.base import basePriceLoad0000r


class load0000r(basePriceLoad0000r):
    """Supply prices from a hand-maintained CSV file.

    Useful for illiquid or obscure tokens (SAI, STAKE, FOAM, …) that automated
    APIs no longer cover.

    The CSV must have at least two columns: ``Asset`` and ``Price``.
    Example::

        Asset,Price
        SAI,1.0
        STAKE,18.50
        FOAM,0.004

    Parameters
    ----------
    csv_path : str
        Path to the CSV file.  If the file does not exist the loader silently
        returns None for every symbol (so it can be listed last as a
        best-effort fallback without crashing the pipeline).
    """

    def __init__(self, csv_path: str = "data/assetPrices.csv"):
        self._csv_path = csv_path
        self._prices: dict[str, float] | None = None   # lazily loaded

    def name(self) -> str:
        return "manual"

    def version(self) -> str:
        return "0.0.1"

    def _ensure_loaded(self) -> None:
        if self._prices is not None:
            return
        self._prices = {}
        if not os.path.exists(self._csv_path):
            print(f"[manual] price file not found: {self._csv_path} — no manual prices available")
            return
        with open(self._csv_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                asset = row.get("Asset", "").strip().upper()
                raw_price = row.get("Price", "").strip()
                if asset and raw_price:
                    try:
                        self._prices[asset] = float(raw_price)
                    except ValueError:
                        print(f"[manual] skipping non-numeric price for {asset}: {raw_price!r}")

    def fetchPrice(self, symbol: str, timestamp: int) -> float | None:
        # timestamp is ignored — the CSV is assumed to already be for the right date
        self._ensure_loaded()
        return self._prices.get(symbol.upper())
