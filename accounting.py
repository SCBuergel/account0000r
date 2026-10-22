"""End-of-year (EOY) portfolio accounting, one step at a time.

    python accounting.py <year> <steps> [--profile NAME] [--workers N]

Steps, in pipeline order (each reads the files the earlier steps wrote):
    0  check that every chain's RPC works and is an archive node
    1  derive accounts from secrets.json           -> data/accounts-blank.json
    2  find the EOY block number of every chain    -> data/chains-<year>-blocks.json
    3  load token decimals from the chains          -> data/chains-<year>-tokens.json
    4  load EOY balances of every account (slow)    -> data/accounts-<year>.json
    5  fetch EOY asset prices                       -> data/assetPrices-<year>.csv
    6  print the portfolio and write summary CSVs   -> data/*_values.csv

Examples:
    python accounting.py 2024 1-6                    full pipeline
    python accounting.py 2024 5,6                    prices and analysis again
    python accounting.py 2024 6 --profile corporate  analysis for the "corporate" accounts
"""

import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import account0000r
import analyz0000r
from load0000rs import ethBalance, metaLoad0000rErc20
from priceLoad0000rs import collectSymbols, defaultPriceLoaders, eoyTimestamp, exportPrices, loadAssetPrices
from rpc import build_web3
from utils import is_non_archive_error, ts_to_utc

SECRETS_FILE = "secrets.json"
CHAINS_FILE = "data/chains.json"
MANUAL_PRICES_FILE = "data/assetPrices-manual.csv"
ACCOUNTS_BLANK_FILE = "data/accounts-blank.json"


class Context:
    """The year being processed, the profile filter, and the files of that year."""

    def __init__(self, year, profile, workers=10):
        self.year = year
        self.profile = profile
        self.workers = workers  # parallel RPC requests in steps 3 and 4
        self.chainsBlocksFile = f"data/chains-{year}-blocks.json"
        self.chainsTokensFile = f"data/chains-{year}-tokens.json"
        self.accountsFile = f"data/accounts-{year}.json"
        self.pricesFile = f"data/assetPrices-{year}.csv"


def requireFile(path, hint):
    if not os.path.exists(path):
        sys.exit(f"ERROR: required file not found: {path}\n  {hint}")


def checkChain(chain):
    """(reachable, archive, message) for one chain. Runs in a thread, so it must not print."""
    try:
        w3 = build_web3(chain)
        latest = w3.eth.get_block("latest")
    except Exception as e:
        return False, False, f"CONNECTIVITY FAILED: {e}"
    msg = f"connectivity OK, latest block {latest.number} ({ts_to_utc(latest.timestamp)})"
    try:
        w3.eth.get_balance("0x0000000000000000000000000000000000000000", 1)
        return True, True, msg
    except Exception as e:
        detail = "NOT an archive node" if is_non_archive_error(e) else f"archive check error: {e}"
        return True, False, f"{msg} | {detail}"


def step0_check_chains(ctx):
    requireFile(CHAINS_FILE, "create it from data/chains-sample.json")
    chains = account0000r.readJson(CHAINS_FILE)
    if not chains:
        sys.exit(f"ERROR: {CHAINS_FILE} lists no chains")
    print(f"step0: checking {len(chains)} chain(s) from {CHAINS_FILE}")
    unreachable, nonArchive = [], []
    with ThreadPoolExecutor(max_workers=len(chains)) as pool:
        futures = {pool.submit(checkChain, c): c["name"] for c in chains}
        for future in as_completed(futures):
            name = futures[future]
            reachable, archive, msg = future.result()
            print(f"  [{name}] {msg}")
            if not reachable:
                unreachable.append(name)
            elif not archive:
                nonArchive.append(name)
    if unreachable:
        print(f"\nERROR: unreachable: {unreachable}. Fix their 'api' URLs in {CHAINS_FILE}.")
    if nonArchive:
        print(f"\nWARNING: not archive nodes: {nonArchive}. Step 4 needs archive endpoints for them.")
    if not unreachable and not nonArchive:
        print(f"step0: all {len(chains)} chain(s) passed")


def step1_derive_accounts(ctx):
    """Writes address/index/mnemonic records without balances. Re-run only when secrets
    change. To manage accounts by hand, write ACCOUNTS_BLANK_FILE yourself instead."""
    requireFile(SECRETS_FILE, "create it from EXAMPLE-secrets.json")
    accounts = account0000r.accountsFromSecrets(account0000r.readJson(SECRETS_FILE))
    account0000r.writeJson(accounts, ACCOUNTS_BLANK_FILE)
    print(f"step1: {len(accounts)} accounts written to {ACCOUNTS_BLANK_FILE}")


def step2_find_eoy_blocks(ctx):
    requireFile(CHAINS_FILE, "create it from data/chains-sample.json")
    chains = account0000r.getBlockNoFromTimestamp(account0000r.readJson(CHAINS_FILE), eoyTimestamp(ctx.year))
    account0000r.writeJson(chains, ctx.chainsBlocksFile)
    print(f"step2: EOY block numbers written to {ctx.chainsBlocksFile}")


def step3_load_token_metadata(ctx):
    """Re-run after adding tokens to chains.json (and step 2, which copies the token list)."""
    requireFile(ctx.chainsBlocksFile, "run step 2 first")
    chains = account0000r.readJson(ctx.chainsBlocksFile)
    _, chains = account0000r.generateTokenLoad0000rs(chains, metaLoad0000rErc20.load0000r(),
                                                     loadChainData=True, atBlock=True, max_workers=ctx.workers)
    account0000r.writeJson(chains, ctx.chainsTokensFile)
    print(f"step3: token metadata written to {ctx.chainsTokensFile}")


def step4_load_eoy_balances(ctx):
    """Always starts from ACCOUNTS_BLANK_FILE and merges in balances already stored in
    the year's accounts file, so only missing balances are fetched. Delete the accounts
    file to fetch everything again."""
    requireFile(ACCOUNTS_BLANK_FILE, "run step 1 first")
    requireFile(ctx.chainsTokensFile, "run step 3 first")
    accounts = account0000r.readJson(ACCOUNTS_BLANK_FILE)
    if os.path.exists(ctx.accountsFile):
        merged = account0000r.mergeCachedChains(accounts, account0000r.readJson(ctx.accountsFile))
        print(f"step4: {len(accounts)} accounts, {merged} with cached balances from {ctx.accountsFile}")
    chains = account0000r.readJson(ctx.chainsTokensFile)
    erc20Loaders, chains = account0000r.generateTokenLoad0000rs(chains, metaLoad0000rErc20.load0000r(),
                                                                loadChainData=False, atBlock=True)
    loaders = [ethBalance.load0000r(atBlock=True, skipAnalysisIfEntryExists=True), *erc20Loaders]
    accounts, errors = account0000r.loadAccountMetadata(loaders, accounts, chains, max_workers=ctx.workers)
    account0000r.writeJson(accounts, ctx.accountsFile)
    print(f"step4: balances written to {ctx.accountsFile}" + (f", {len(errors)} errors (see above)" if errors else ""))


def step5_load_eoy_prices(ctx):
    """Prices already in the year's price file are kept; only new symbols are fetched
    (on-chain sources first, then the APIs). Delete the price file to fetch everything
    again. Add assets no source knows to MANUAL_PRICES_FILE."""
    requireFile(ctx.accountsFile, "run step 4 first")
    requireFile(ctx.chainsTokensFile, "run step 3 first")
    chains = account0000r.readJson(ctx.chainsTokensFile)
    symbols = collectSymbols(account0000r.readJson(ctx.accountsFile), chains)
    loaders = defaultPriceLoaders(MANUAL_PRICES_FILE, chains, cacheCsv=ctx.pricesFile)
    prices = loadAssetPrices(symbols, eoyTimestamp(ctx.year), loaders)
    exportPrices(prices, ctx.pricesFile)
    print(f"step5: {len(prices)} of {len(symbols)} prices written to {ctx.pricesFile}")


def step6_portfolio_analysis(ctx):
    """Reads only local files, safe to re-run at any time."""
    requireFile(ctx.accountsFile, "run step 4 first")
    requireFile(ctx.chainsTokensFile, "run step 3 first")
    requireFile(ctx.pricesFile, "run step 5 first")
    accounts = account0000r.readJson(ctx.accountsFile)
    print(f"step6: profiles in {ctx.accountsFile}: {sorted({a.get('profile', '(none)') for a in accounts})}")
    accounts = account0000r.filterByProfile(accounts, ctx.profile)
    chains = account0000r.readJson(ctx.chainsTokensFile)
    analyz0000r.portfolioValue(accounts, chains, atBlock=True, assetPricesCsv=ctx.pricesFile)


STEPS = [
    ("check chain RPCs", step0_check_chains),
    ("derive accounts", step1_derive_accounts),
    ("find EOY block numbers", step2_find_eoy_blocks),
    ("load token metadata", step3_load_token_metadata),
    ("load EOY balances (slow)", step4_load_eoy_balances),
    ("fetch EOY prices", step5_load_eoy_prices),
    ("portfolio analysis", step6_portfolio_analysis),
]


def parseSteps(raw):
    """"0-3,5" -> [0, 1, 2, 3, 5]. Raises ValueError for anything outside 0..len(STEPS)-1."""
    steps = set()
    for token in raw.replace(" ", "").split(","):
        if not token:
            continue
        lo, _, hi = token.partition("-")
        lo, hi = int(lo), int(hi or lo)
        if not 0 <= lo <= hi < len(STEPS):
            raise ValueError(f"invalid step range '{token}', valid steps are 0..{len(STEPS) - 1}")
        steps.update(range(lo, hi + 1))
    return sorted(steps)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("year", type=int, help="year to account for, e.g. 2024")
    parser.add_argument("steps", help="steps to run, e.g. 1-6 or 0 or 1,3,5")
    parser.add_argument("--profile", default="personal",
                        help="only analyse accounts with this profile (default: personal); "
                             "accounts without a profile are always included")
    parser.add_argument("--workers", type=int, default=10,
                        help="parallel RPC requests while loading balances (default: 10); "
                             "lower it if endpoints answer 429, raise it while the diagnostics show rpc near 100%%")
    args = parser.parse_args()
    try:
        steps = parseSteps(args.steps)
    except ValueError as e:
        parser.error(str(e))
    ctx = Context(args.year, args.profile, args.workers)
    for n in steps:
        desc, fn = STEPS[n]
        print(f"\n{'-' * 60}\n  step {n}: {desc} (year={ctx.year})\n{'-' * 60}\n")
        fn(ctx)
    print(f"\nDone, ran {len(steps)} step(s).")


if __name__ == "__main__":
    main()
