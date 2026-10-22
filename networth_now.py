"""Current net worth of all accounts: today's balances at today's prices.

    python networth_now.py [--refresh] [--profile NAME] [--workers N]

Reads data/accounts-blank.json (written by `accounting.py <year> 1`) and data/chains.json,
then prints the portfolio and writes data/*_values.csv like accounting.py step 6.

Re-runs reuse what is on disk and only fetch what is missing:
    data/chains-now-tokens.json   token decimals (rebuilt when data/chains.json is newer)
    data/accounts-now.json        balances (accounts, chains or tokens without an entry are fetched)
    data/assetPrices-now.csv      prices (only symbols without a price hit the APIs)
Reused values are as old as the run that fetched them. --refresh ignores all three.
"""

import argparse
import os
import time

import account0000r
import diagnostics
import analyz0000r
from accounting import ACCOUNTS_BLANK_FILE, CHAINS_FILE, MANUAL_PRICES_FILE, requireFile
from load0000rs import ethBalance, metaLoad0000rErc20
from priceLoad0000rs import collectSymbols, defaultPriceLoaders, exportPrices, loadAssetPrices

CHAINS_TOKENS_FILE = "data/chains-now-tokens.json"
ACCOUNTS_FILE = "data/accounts-now.json"
PRICES_FILE = "data/assetPrices-now.csv"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--refresh", action="store_true", help="fetch everything again instead of reusing cached files")
    parser.add_argument("--profile", default=None, help="only analyse accounts with this profile (default: all)")
    parser.add_argument("--workers", type=int, default=10,
                        help="parallel RPC requests while loading balances (default: 10); "
                             "lower it if endpoints answer 429, raise it while the diagnostics show rpc near 100%%")
    args = parser.parse_args()
    reuse = not args.refresh

    requireFile(ACCOUNTS_BLANK_FILE, "run `python accounting.py <year> 1` first")
    requireFile(CHAINS_FILE, "create it from data/chains-sample.json")
    accounts = account0000r.readJson(ACCOUNTS_BLANK_FILE)
    if reuse and os.path.exists(ACCOUNTS_FILE):
        merged = account0000r.mergeCachedChains(accounts, account0000r.readJson(ACCOUNTS_FILE))
        print(f"reusing balances of {merged}/{len(accounts)} account(s) from {ACCOUNTS_FILE}")

    tokensCached = (reuse and os.path.exists(CHAINS_TOKENS_FILE)
                    and os.path.getmtime(CHAINS_TOKENS_FILE) >= os.path.getmtime(CHAINS_FILE))
    chains = account0000r.readJson(CHAINS_TOKENS_FILE if tokensCached else CHAINS_FILE)
    erc20Loaders, chains = account0000r.generateTokenLoad0000rs(
        chains, metaLoad0000rErc20.load0000r(), loadChainData=not tokensCached, atBlock=False,
        max_workers=args.workers)
    account0000r.writeJson(chains, CHAINS_TOKENS_FILE)

    loaders = [ethBalance.load0000r(atBlock=False, skipAnalysisIfEntryExists=reuse), *erc20Loaders]
    accounts, _errors = account0000r.loadAccountMetadata(loaders, accounts, chains, max_workers=args.workers)
    account0000r.writeJson(accounts, ACCOUNTS_FILE)
    print(f"balances written to {ACCOUNTS_FILE}")

    symbols = collectSymbols(accounts, chains)
    loaders = defaultPriceLoaders(MANUAL_PRICES_FILE, chains, cacheCsv=PRICES_FILE if reuse else None)
    prices = loadAssetPrices(symbols, int(time.time()), loaders)
    exportPrices(prices, PRICES_FILE)

    accounts = account0000r.filterByProfile(accounts, args.profile)
    analyz0000r.portfolioValue(accounts, chains, atBlock=False, assetPricesCsv=PRICES_FILE)
    print(f"\n{diagnostics.summary()}")


if __name__ == "__main__":
    main()
