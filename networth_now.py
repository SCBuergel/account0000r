"""Quick CURRENT net-worth report for the account0000r repo.

Run from the repo root:  python networth_now.py

It loads current native + ERC-20 balances for every account on every chain,
fetches current USD prices, and prints/writes:
  - total portfolio value
  - value per token   -> data/asset_values.csv
  - value per address -> data/address_values.csv
  - full line items   -> data/account_balances.csv

Incremental re-runs
-------------------
With REUSE_PRIOR = True (default) a re-run reuses whatever is already on disk
and only fetches what is missing:
  - token metadata (decimals/symbols) from data/chains-with-tokens.json
    (auto-rebuilt if data/chains.json is newer, e.g. you edited endpoints/tokens)
  - balances from the most recent data/accounts-*.json snapshot
    (only accounts/chains/tokens without a stored entry are queried again)
  - prices from data/assetPrices-now.csv (only missing symbols hit the APIs)

To force a full refresh: set REUSE_PRIOR = False, or delete the relevant cache
file (data/chains-with-tokens.json / data/assetPrices-now.csv / the newest
data/accounts-*.json).  Note: reused balances/prices are as-of the last run, so
a reuse trades freshness for speed.

Point ACCOUNTS_FILE / CHAINS_FILE at your local files before running.
"""

import glob
import json
import os
import time

import account0000r
import analyz0000r
from load0000rs import ethBalance, metaLoad0000rErc20
from priceLoad0000rs import loadAssetPrices, collectSymbols, exportPrices
from priceLoad0000rs.cryptocompare import load0000r as CryptoCompare
from priceLoad0000rs.coingecko import load0000r as CoinGecko
from priceLoad0000rs.aliases import load0000r as Aliases
from priceLoad0000rs.manual import load0000r as Manual

# ---------------------------------------------------------------------------
# config
# ---------------------------------------------------------------------------
ACCOUNTS_FILE = "accounts-blank.json"       # your local account list
CHAINS_FILE = "data/chains.json"            # your RPCs + token lists
atBlock = False                             # False = current/latest, not EOY

REUSE_PRIOR = True                          # reuse cached data on re-runs (see docstring)

CHAINS_CACHE = "data/chains-with-tokens.json"
PRICES_CSV = "data/assetPrices-now.csv"
DATA_DIR = "data"


def _latest_snapshot(data_dir=DATA_DIR):
    """Return the newest data/accounts-<timestamp>.json snapshot, or None.

    Only files whose name is 'accounts-' followed by a digit (the timestamp)
    are considered, so accounts-blank*.json and other files are ignored.
    """
    candidates = [
        f for f in glob.glob(os.path.join(data_dir, "accounts-*.json"))
        if os.path.basename(f)[len("accounts-"):len("accounts-") + 1].isdigit()
    ]
    return max(candidates, key=os.path.getmtime) if candidates else None


# ---------------------------------------------------------------------------
# 1. load accounts; seed them with prior balances so re-runs can skip
# ---------------------------------------------------------------------------
accounts = json.load(open(ACCOUNTS_FILE))

if REUSE_PRIOR:
    prior = _latest_snapshot()
    if prior:
        cached = {a["address"].lower(): a.get("chains", {}) for a in json.load(open(prior))}
        reused = 0
        for a in accounts:
            ch = cached.get(a["address"].lower())
            if ch:
                a["chains"] = ch
                reused += 1
        print(f"reusing balances for {reused}/{len(accounts)} account(s) from {prior}")

# ---------------------------------------------------------------------------
# 2. load chains; reuse token metadata unless chains.json is newer
# ---------------------------------------------------------------------------
use_chain_cache = (
    REUSE_PRIOR
    and os.path.exists(CHAINS_CACHE)
    and os.path.getmtime(CHAINS_CACHE) >= os.path.getmtime(CHAINS_FILE)
)
if use_chain_cache:
    chains = json.load(open(CHAINS_CACHE))
    load_chain_data = False
    print(f"reusing token metadata from {CHAINS_CACHE}")
else:
    chains = json.load(open(CHAINS_FILE))
    load_chain_data = True
    if REUSE_PRIOR and os.path.exists(CHAINS_CACHE):
        print(f"{CHAINS_FILE} is newer than the cache — reloading token metadata")

metaErc20 = metaLoad0000rErc20.load0000r()
erc20Loaders, chains = account0000r.generateTokenLoad0000rs(
    chains, metaErc20, loadChainData=load_chain_data, atBlock=atBlock
)
# refresh the cache so the next run can skip the on-chain decimals lookup
account0000r.writeJson(chains, CHAINS_CACHE)

# ---------------------------------------------------------------------------
# 3. fetch native + ERC-20 balances (skips entries already present), then store
# ---------------------------------------------------------------------------
# ERC-20 loaders already skip when an entry exists; make the native loader match.
loaders = [
    ethBalance.load0000r(atBlock=atBlock, skipAnalysisIfEntryExists=REUSE_PRIOR),
    *erc20Loaders,
]
accounts, errors = account0000r.loadAccountMetadata(loaders, accounts, chains)
snapshot = account0000r.writeJson(accounts)
print("balances saved to", snapshot)

# ---------------------------------------------------------------------------
# 4. fetch prices for every symbol present (reuse prior prices, fetch missing)
# ---------------------------------------------------------------------------
symbols = collectSymbols(accounts, chains)
priceLoaders = []
if REUSE_PRIOR and os.path.exists(PRICES_CSV):
    # reuse already-fetched prices first; only unpriced symbols reach the APIs
    priceLoaders.append(Manual(PRICES_CSV))
    print(f"reusing prices from {PRICES_CSV} (delete it to force a full price refresh)")
priceLoaders += [
    CryptoCompare(),
    CoinGecko(symbol_overrides={
        "ETH": "ethereum", "WETH": "weth", "USDC": "usd-coin",
        "USDT": "tether", "DAI": "dai", "WBTC": "wrapped-bitcoin",
        "XDAI": "xdai", "GNO": "gnosis", "MATIC": "matic-network",
        "BNB": "binancecoin", "COW": "cow-protocol",
    }),
    Aliases({"XHOPR": "HOPR", "WXHOPR": "HOPR", "STETH": "ETH",
             "WETH": "ETH", "USDC.E": "USDC"}),
    Manual("data/assetPrices-manual.csv"),
]
prices = loadAssetPrices(symbols, int(time.time()), priceLoaders)
exportPrices(prices, PRICES_CSV)

# ---------------------------------------------------------------------------
# 5. analyze: total + per-token + per-address (also writes 3 CSVs)
# ---------------------------------------------------------------------------
analyz0000r.portfolioValue(
    accounts, chains, atBlock=atBlock, assetPricesCsv=PRICES_CSV
)
