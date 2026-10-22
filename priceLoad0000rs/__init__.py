"""Price pipeline: collect the symbols that appear in loaded accounts, then price them
with a list of loaders tried in order (the first price found for a symbol wins).

    loaders = defaultPriceLoaders("data/assetPrices-manual.csv", chains, cacheCsv="data/assetPrices-2024.csv")
    symbols = collectSymbols(accounts, chains)
    prices = loadAssetPrices(symbols, eoyTimestamp(2024), loaders)
    exportPrices(prices, "data/assetPrices-2024.csv")
"""

import csv
import os
from datetime import datetime, timezone

from priceLoad0000rs import aliases, chainlink, coingecko, cryptocompare, manual, stable, uniswap
from load0000rs import metaLoad0000rErc20


def eoyTimestamp(year):
    """Midnight UTC on Jan 1 of year + 1, the end-of-year snapshot. eoyTimestamp(2024) == 1735689600."""
    return int(datetime(year + 1, 1, 1, tzinfo=timezone.utc).timestamp())


def collectSymbols(accounts, chains):
    """Sorted upper-case symbols of every chain's native asset and of every ERC-20 token
    with a non-zero balance in `accounts`."""
    symbols = {c["nativeAsset"].upper() for c in chains if c.get("nativeAsset")}
    for account in accounts:
        for chainData in account.get("chains", {}).values():
            for entry in chainData.get(metaLoad0000rErc20.NAME, {}).values():
                token = entry.get("erc20Balance", {})
                if token.get("balance", 0) > 0 and token.get("symbol"):
                    symbols.add(token["symbol"].upper())
    return sorted(symbols)


def defaultPriceLoaders(manualCsv, chains, cacheCsv=None):
    """The standard loader order: prices cached by an earlier run (if cacheCsv exists),
    stablecoins at 1 USD, the on-chain sources (Chainlink feeds, then Uniswap pools, read
    through the RPCs of `chains`), aliases of wrapped tokens, the price APIs, then the
    hand-maintained CSV."""
    loaders = [manual.load0000r(cacheCsv)] if cacheCsv and os.path.exists(cacheCsv) else []
    return loaders + [stable.load0000r(), chainlink.load0000r(chains), uniswap.load0000r(chains),
                      aliases.load0000r(), cryptocompare.load0000r(), coingecko.load0000r(),
                      manual.load0000r(manualCsv)]


def loadAssetPrices(symbols, timestamp, loaders):
    """symbol -> USD price for every symbol some loader could price. Unpriced symbols are
    printed as a warning and left out."""
    prices = {}
    remaining = list(symbols)
    for loader in loaders:
        if not remaining:
            break
        print(f"[loadAssetPrices] trying {loader.name()} for {len(remaining)} symbol(s): {remaining}")
        fetched, remaining = loader.load(remaining, timestamp, resolved=prices)
        prices.update(fetched)
        for sym, price in sorted(fetched.items()):
            print(f"  {sym}: ${price:,.4f}")
    if remaining:
        print(f"\nWARNING: no price for {len(remaining)} asset(s): {remaining}\n"
              f"  Add them to the manual price CSV and re-run.")
    return prices


def exportPrices(prices, filename):
    """Write an Asset,Price CSV, the format read by manual.load0000r and analyz0000r.portfolioValue."""
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Asset", "Price"])
        for asset, price in sorted(prices.items()):
            writer.writerow([asset, price])
