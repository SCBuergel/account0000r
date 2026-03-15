"""priceLoad0000rs — EOY asset price loading pipeline.

Usage example::

    from priceLoad0000rs import loadAssetPrices, collectSymbols, eoyTimestamp, exportPrices
    from priceLoad0000rs.cryptocompare import load0000r as CryptoCompare
    from priceLoad0000rs.coingecko import load0000r as CoinGecko
    from priceLoad0000rs.manual import load0000r as Manual

    loaders = [CryptoCompare(), CoinGecko(), Manual("data/assetPrices.csv")]

    symbols = collectSymbols(accounts, chains)
    ts = eoyTimestamp(2024)
    prices = loadAssetPrices(symbols, ts, loaders)
    exportPrices(prices, "data/assetPrices-EOY2024.csv")
"""

import csv
from datetime import datetime, timezone

from priceLoad0000rs.base import basePriceLoad0000r


def eoyTimestamp(year: int) -> int:
    """Return the Unix timestamp for midnight UTC on Jan 1 of *year + 1*.

    This is the conventional "end of year *year*" snapshot used by the
    CryptoCompare histoday endpoint's ``toTs`` parameter.

    Example: eoyTimestamp(2024) → 1735689600 (2025-01-01 00:00:00 UTC)
    """
    dt = datetime(year + 1, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    return int(dt.timestamp())


def collectSymbols(accounts: list, chains: list) -> list[str]:
    """Derive the set of asset symbols that appear in *accounts* / *chains*.

    Scans:
    - ``chains[*].nativeAsset`` for native coins (ETH, MATIC, …)
    - ``accounts[*].chains[*]["ERC20 balances"][*].erc20Balance.symbol`` for
      ERC-20 tokens with a non-zero balance

    Returns a sorted, deduplicated list of uppercase symbols.
    """
    symbols: set[str] = set()

    # Native assets from chain definitions
    for chain in chains:
        native = chain.get("nativeAsset")
        if native:
            symbols.add(native.upper())

    # ERC-20 tokens from loaded account data
    for account in accounts:
        for chain_data in account.get("chains", {}).values():
            erc20_section = chain_data.get("ERC20 balances", {})
            for token_entry in erc20_section.values():
                erc20 = token_entry.get("erc20Balance", {})
                if erc20.get("balance", 0) > 0:
                    sym = erc20.get("symbol")
                    if sym:
                        symbols.add(sym.upper())

    return sorted(symbols)


def loadAssetPrices(
    symbols: list[str],
    timestamp: int,
    loaders: list[basePriceLoad0000r],
) -> dict[str, float]:
    """Fetch USD prices for *symbols* at *timestamp* using *loaders* in order.

    For each symbol the loaders are tried in order; the first successful price
    is used.  Symbols that no loader can price are logged as warnings.

    Parameters
    ----------
    symbols : list[str]
        Uppercase asset tickers to price (e.g. ["ETH", "USDC", "GNO"]).
    timestamp : int
        Unix timestamp representing the target date (use ``eoyTimestamp()``).
    loaders : list[basePriceLoad0000r]
        Ordered list of price loaders.  Earlier loaders take precedence.

    Returns
    -------
    dict[str, float]
        Mapping of symbol → USD price.  Symbols with no price found are absent.
    """
    prices: dict[str, float] = {}
    remaining = list(symbols)

    for loader in loaders:
        if not remaining:
            break
        print(f"[loadAssetPrices] trying {loader.name()} for {len(remaining)} symbol(s): {remaining}")
        fetched, remaining = loader.load(remaining, timestamp)
        prices.update(fetched)
        if fetched:
            print(f"[loadAssetPrices] {loader.name()} resolved: {sorted(fetched)}")

    if remaining:
        print(
            f"\nWARNING: no price found for {len(remaining)} asset(s): {remaining}\n"
            f"  Add them to a manual CSV or provide a symbol_overrides mapping for CoinGecko."
        )

    return prices


def exportPrices(prices: dict, filename: str) -> None:
    """Write *prices* to a CSV file in the Asset,Price format consumed by portfolioValue().

    Parameters
    ----------
    prices : dict[str, float]
        Symbol → USD price mapping, as returned by loadAssetPrices.
    filename : str
        Output path, e.g. "data/assetPrices-EOY2024.csv".
    """
    with open(filename, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Asset", "Price"])
        for asset, price in prices.items():
            writer.writerow([asset, price])
