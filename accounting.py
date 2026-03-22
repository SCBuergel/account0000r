"""
accounting.py — step-by-step EOY portfolio accounting

Usage:
    python accounting.py <year> <step> [<step> ...]

Steps (run in the order listed):
    step0  — check chain RPC connectivity and archive support
    step1  — derive HD wallet accounts from secrets.json
    step2  — find EOY block numbers for every chain
    step3  — load on-chain token metadata (decimals, symbols)
    step4  — load EOY balances for every account (slow, hits RPCs)
    step5  — fetch EOY asset prices
    step6  — print portfolio analysis

Examples:
    python accounting.py 2024 step1 step2 step3 step4 step5 step6
    python accounting.py 2024 step5 step6          # re-run prices + analysis only
    python accounting.py 2024 step0                 # just check RPC health
"""

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from web3 import Web3
import account0000r
import analyz0000r
from load0000rs import ethBalance, metaLoad0000rErc20
from priceLoad0000rs import loadAssetPrices, collectSymbols, eoyTimestamp, exportPrices
from priceLoad0000rs.cryptocompare import load0000r as CryptoCompare
from priceLoad0000rs.coingecko   import load0000r as CoinGecko
from priceLoad0000rs.aliases     import load0000r as Aliases
from priceLoad0000rs.manual      import load0000r as Manual
from utils import ts_to_utc, _is_non_archive_error


# ─── Configuration ────────────────────────────────────────────────────────────

# Input files (edit to match your setup)
SECRETS_FILE       = "secrets.json"
CHAINS_FILE        = "data/chains.json"
MANUAL_PRICES_FILE = "data/assetPrices-manual.csv"   # hand-maintained prices for obscure tokens

# Intermediate and output files (auto-named by year; set in _init_paths)
ACCOUNTS_BLANK_FILE = None
CHAINS_BLOCKS_FILE  = None
CHAINS_TOKENS_FILE  = None
ACCOUNTS_FILE       = None
PRICES_FILE         = None


def _init_paths(year):
    global ACCOUNTS_BLANK_FILE, CHAINS_BLOCKS_FILE, CHAINS_TOKENS_FILE
    global ACCOUNTS_FILE, PRICES_FILE
    ACCOUNTS_BLANK_FILE = "data/accounts-blank.json"
    CHAINS_BLOCKS_FILE  = f"data/chains-{year}-blocks.json"
    CHAINS_TOKENS_FILE  = f"data/chains-{year}-tokens.json"
    ACCOUNTS_FILE       = f"data/accounts-{year}.json"
    PRICES_FILE         = f"data/assetPrices-{year}.csv"


# Derived tokens that share the price of their underlying asset.
# Add any project-specific mappings here.
PRICE_ALIASES = {
    "XHOPR":   "HOPR",
    "WXHOPR":  "HOPR",
    "STKAAVE": "AAVE",
    "STETH":   "ETH",
    "WETH":    "ETH",
    "WBTC":    "BTC",
    "XDAI":    "DAI",
    "USDC.E":  "USDC",
}


def _require_file(path, producing_step):
    """Exit with a helpful message if a required file is missing."""
    if not os.path.exists(path):
        print(f"ERROR: required file not found: {path}")
        print(f"  → Run {producing_step} first to generate it.")
        sys.exit(1)


# ─── Steps ────────────────────────────────────────────────────────────────────

def _check_single_chain(chain):
    """Worker: probe one chain for connectivity and archive capability.
    Returns (connectivity_ok, archive_ok, detail_message).
    Runs in a thread — must not print directly.
    """
    name = chain["name"]
    api  = chain["api"]

    try:
        w3     = Web3(Web3.HTTPProvider(api))
        latest = w3.eth.get_block("latest")
    except Exception as e:
        return False, False, f"CONNECTIVITY FAILED — {e}"

    conn_msg = f"connectivity OK — latest block {latest.number} ({ts_to_utc(latest.timestamp)})"

    try:
        w3.eth.get_balance("0x0000000000000000000000000000000000000000", 1)
        return True, True, conn_msg
    except Exception as e:
        if _is_non_archive_error(e):
            arch_msg = "NOT an archive node"
        else:
            arch_msg = f"archive check error — {e}"
        return True, False, f"{conn_msg} | {arch_msg}"


def step0_check_chains():
    """Verify that every chain in CHAINS_FILE has a working RPC provider
    with archive capabilities.

    All chains are probed in parallel.  Each request is logged the moment it
    is dispatched; results are printed as they arrive.

    Checks two things per chain:
      1. Basic connectivity — can the RPC be reached and return the latest block?
      2. Archive capability — can it serve historical state (required for step4)?
    """
    _require_file(CHAINS_FILE, "step0 requires chains.json — create it from data/chains-sample.json")
    chains = json.load(open(CHAINS_FILE))
    print(f"step0: checking {len(chains)} chain(s) from {CHAINS_FILE}")

    failed_connectivity = []
    failed_archive      = []

    with ThreadPoolExecutor(max_workers=len(chains)) as executor:
        futures = {}
        for chain in chains:
            print(f"  [{chain['name']}] sending request...")
            futures[executor.submit(_check_single_chain, chain)] = chain["name"]

        for future in as_completed(futures):
            name = futures[future]
            conn_ok, arch_ok, msg = future.result()
            print(f"  [{name}] {msg}")
            if not conn_ok:
                failed_connectivity.append(name)
            elif not arch_ok:
                failed_archive.append(name)

    # ── summary ───────────────────────────────────────────────────────────────
    print()
    if not failed_connectivity and not failed_archive:
        print(f"step0: all {len(chains)} chain(s) passed\n")
        return

    if failed_connectivity:
        print(f"ERROR: {len(failed_connectivity)} chain(s) unreachable — step4 will not work for these:")
        for name in failed_connectivity:
            print(f"  - {name}")
        print(f"  → Check the 'api' URL for these chains in {CHAINS_FILE}\n")

    if failed_archive:
        print(f"WARNING: {len(failed_archive)} chain(s) have non-archive RPC providers — step4 requires archive nodes:")
        for name in failed_archive:
            print(f"  - {name}")
        print(f"  → Replace the 'api' value for these chains in {CHAINS_FILE}")
        print(f"    with an archive endpoint (e.g. Alchemy, Infura, or a self-hosted archive node)\n")


def step1_derive_accounts():
    """Derive HD wallet accounts from secrets.json and save to ACCOUNTS_BLANK_FILE.

    Writes plain address/index/mnemonic records with no balance data.  This
    file is the stable seed used by step4 — re-run step1 only when adding
    mnemonics or changing the number of derived accounts.

    If you manage accounts manually rather than from a mnemonic, skip this
    step and write a JSON list directly to ACCOUNTS_BLANK_FILE instead
    (see README for the required format).
    """
    _require_file(SECRETS_FILE, "step1 requires secrets.json — create it from EXAMPLE-secrets.json")
    secrets  = json.load(open(SECRETS_FILE))
    accounts = account0000r.accountsFromSecrets(secrets)

    account0000r.writeJson(accounts, ACCOUNTS_BLANK_FILE)
    print(f"step1: {len(accounts)} accounts written to {ACCOUNTS_BLANK_FILE}")


def step2_find_eoy_blocks():
    """Look up the block number closest to EOY midnight for every chain.

    Reads CHAINS_FILE, performs a binary search on each chain's RPC, and
    writes the results to CHAINS_BLOCKS_FILE.  Only needs to run once per year.
    The resulting file is the input for step3 and step4.
    """
    _require_file(CHAINS_FILE, "step2 requires chains.json — create it from data/chains-sample.json")
    chains    = json.load(open(CHAINS_FILE))
    timestamp = eoyTimestamp(EOY_YEAR)

    chains = account0000r.getBlockNoFromTimestamp(chains, timestamp)

    account0000r.writeJson(chains, CHAINS_BLOCKS_FILE)
    print(f"step2: EOY block numbers written to {CHAINS_BLOCKS_FILE}")


def step3_load_token_metadata():
    """Fetch on-chain token metadata (decimals, canonical symbol) for all tokens
    listed in CHAINS_BLOCKS_FILE and save to CHAINS_TOKENS_FILE.

    Re-run whenever you add a new token to chains.json.  For subsequent runs
    the saved CHAINS_TOKENS_FILE already contains the metadata so you can pass
    loadChainData=False to generateTokenLoad0000rs to skip the RPC calls.
    """
    _require_file(CHAINS_BLOCKS_FILE, "step2 (finds EOY block numbers)")
    chains   = json.load(open(CHAINS_BLOCKS_FILE))
    metaErc20 = metaLoad0000rErc20.load0000r()

    _erc20Loaders, chains = account0000r.generateTokenLoad0000rs(
        chains, metaErc20, loadChainData=True, atBlock=True
    )

    account0000r.writeJson(chains, CHAINS_TOKENS_FILE)
    print(f"step3: token metadata written to {CHAINS_TOKENS_FILE}")


def step4_load_eoy_balances():
    """Load native coin and ERC-20 balances at the EOY block for every account
    on every chain and save the enriched account list to ACCOUNTS_FILE.

    This is the slowest step — it makes one RPC call per account per token per
    chain.  Re-running is safe: existing entries are kept and any missing ones
    are filled in.  To force a full re-fetch, delete ACCOUNTS_FILE first and
    re-run — it will restart from the blank accounts in ACCOUNTS_BLANK_FILE.
    """
    source = ACCOUNTS_FILE if os.path.exists(ACCOUNTS_FILE) else ACCOUNTS_BLANK_FILE
    _require_file(source, "step1 (derives accounts)" if source == ACCOUNTS_BLANK_FILE else "step4 (previous run)")
    _require_file(CHAINS_TOKENS_FILE, "step3 (loads token metadata)")
    print(f"step4: loading accounts from {source}")
    accounts  = json.load(open(source))
    chains    = json.load(open(CHAINS_TOKENS_FILE))
    metaErc20 = metaLoad0000rErc20.load0000r()

    erc20Loaders, chains = account0000r.generateTokenLoad0000rs(
        chains, metaErc20, loadChainData=False, atBlock=True
    )

    loaders = [ethBalance.load0000r(atBlock=True), *erc20Loaders]
    accounts, errors = account0000r.loadAccountMetadata(loaders, accounts, chains)

    account0000r.writeJson(accounts, ACCOUNTS_FILE)
    print(f"step4: balances written to {ACCOUNTS_FILE}")
    if errors:
        print(f"  {len(errors)} errors encountered (see above)")


def step5_load_eoy_prices():
    """Fetch EOY closing prices for every asset that appears in ACCOUNTS_FILE
    and save them to PRICES_FILE.

    Loader priority: CryptoCompare → CoinGecko → Aliases → Manual CSV.
    Add any assets that APIs cannot find to MANUAL_PRICES_FILE as Asset,Price
    rows and re-run this step.
    """
    _require_file(ACCOUNTS_FILE, "step4 (loads EOY balances)")
    _require_file(CHAINS_TOKENS_FILE, "step3 (loads token metadata)")
    accounts = json.load(open(ACCOUNTS_FILE))
    chains   = json.load(open(CHAINS_TOKENS_FILE))

    symbols = collectSymbols(accounts, chains)
    print(f"step5: pricing {len(symbols)} symbols: {symbols}")

    loaders = [
        CryptoCompare(),
        CoinGecko(),
        Aliases(PRICE_ALIASES),
        Manual(MANUAL_PRICES_FILE),
    ]

    prices = loadAssetPrices(symbols, eoyTimestamp(EOY_YEAR), loaders)
    exportPrices(prices, PRICES_FILE)
    print(f"step5: {len(prices)}/{len(symbols)} prices written to {PRICES_FILE}")


def step6_portfolio_analysis():
    """Print a full portfolio overview and write summary CSVs to data/.

    Reads balances from ACCOUNTS_FILE and prices from PRICES_FILE.
    Safe to re-run at any time without touching RPC endpoints or price APIs.
    """
    _require_file(ACCOUNTS_FILE, "step4 (loads EOY balances)")
    _require_file(CHAINS_TOKENS_FILE, "step3 (loads token metadata)")
    _require_file(PRICES_FILE, "step5 (fetches EOY prices)")
    accounts = json.load(open(ACCOUNTS_FILE))
    chains   = json.load(open(CHAINS_TOKENS_FILE))

    analyz0000r.portfolioValue(
        accounts, chains,
        atBlock=True,
        assetPricesCsv=PRICES_FILE,
    )


# ─── CLI ──────────────────────────────────────────────────────────────────────

STEPS = {
    "step0": ("check chain RPCs",            step0_check_chains),
    "step1": ("derive accounts",             step1_derive_accounts),
    "step2": ("find EOY block numbers",      step2_find_eoy_blocks),
    "step3": ("load token metadata",         step3_load_token_metadata),
    "step4": ("load EOY balances (slow)",    step4_load_eoy_balances),
    "step5": ("fetch EOY prices",            step5_load_eoy_prices),
    "step6": ("portfolio analysis",          step6_portfolio_analysis),
}


def main():
    parser = argparse.ArgumentParser(
        description="Step-by-step EOY portfolio accounting.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\n".join(f"  {k}  — {desc}" for k, (desc, _) in STEPS.items()),
    )
    parser.add_argument("year", type=int, help="EOY year to process (e.g. 2024)")
    parser.add_argument(
        "steps", nargs="+", choices=list(STEPS.keys()), metavar="step",
        help="one or more steps to run: " + ", ".join(STEPS.keys()),
    )

    args = parser.parse_args()
    _init_paths(args.year)

    # make EOY_YEAR available to step functions that reference it via eoyTimestamp()
    global EOY_YEAR
    EOY_YEAR = args.year

    for step_name in args.steps:
        desc, fn = STEPS[step_name]
        print(f"\n{'─' * 60}")
        print(f"  {step_name}: {desc}  (year={args.year})")
        print(f"{'─' * 60}\n")
        fn()

    print(f"\nDone — ran {len(args.steps)} step(s).")


if __name__ == "__main__":
    main()
