"""Prices from a hand-maintained Asset,Price CSV, for tokens no API covers (SAI, STAKE, ...).

A missing file yields no prices and no error, so the loader can always be listed last.
The same loader also serves cached prices from an earlier run.
"""

import csv
import os

from priceLoad0000rs.base import basePriceLoad0000r


def readPriceCsv(path):
    """Asset -> price dict from a CSV with Asset and Price columns. Bad rows are skipped
    with a warning; a missing file gives an empty dict."""
    prices = {}
    if not os.path.exists(path):
        print(f"[manual] no price file at {path}")
        return prices
    with open(path, newline="") as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        headers = [h.strip() for h in reader.fieldnames or []]
        if "Asset" not in headers or "Price" not in headers:
            print(f"[manual] ERROR: {path} needs 'Asset' and 'Price' columns, found {headers}")
            return prices
        for lineno, row in enumerate(reader, start=2):
            row = {k.strip(): (v or "").strip() for k, v in row.items()}
            try:
                prices[row["Asset"].upper()] = float(row["Price"])
            except (KeyError, ValueError):
                print(f"[manual] WARNING: {path}:{lineno} skipped, not an Asset,Price row: {row}")
    print(f"[manual] {len(prices)} price(s) from {path}")
    return prices


class load0000r(basePriceLoad0000r):
    def __init__(self, csv_path="data/assetPrices.csv"):
        self._csv_path = csv_path
        self._prices = None  # read on first use

    def name(self):
        return "manual"

    def version(self):
        return "0.0.1"

    def fetchPrice(self, symbol, timestamp):
        if self._prices is None:
            self._prices = readPriceCsv(self._csv_path)
        return self._prices.get(symbol.upper())  # the CSV is assumed to match the date
