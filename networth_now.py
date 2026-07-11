"""Quick CURRENT net-worth report for the account0000r repo.

Run from the repo root:  python networth_now.py

It loads current native + ERC-20 balances for every account on every chain,
fetches current USD prices, and prints/writes:
  - total portfolio value
  - value per token   -> data/asset_values.csv
  - value per address -> data/address_values.csv
  - full line items   -> data/account_balances.csv

Point ACCOUNTS_FILE / CHAINS_FILE at your local files before running.
"""

import json
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

# First run: True (reads each token's decimals on-chain, slow but one-off).
# After the first run you can load data/chains-with-tokens.json and set False.
LOAD_CHAIN_DATA = True

# ---------------------------------------------------------------------------
# 1. load accounts + chains
# ---------------------------------------------------------------------------
accounts = json.load(open(ACCOUNTS_FILE))
chains = json.load(open(CHAINS_FILE))

# ---------------------------------------------------------------------------
# 2. build one ERC-20 loader per token
# ---------------------------------------------------------------------------
metaErc20 = metaLoad0000rErc20.load0000r()
erc20Loaders, chains = account0000r.generateTokenLoad0000rs(
    chains, metaErc20, loadChainData=LOAD_CHAIN_DATA, atBlock=atBlock
)
# cache enriched chains so future runs can skip the on-chain decimals lookup
account0000r.writeJson(chains, "data/chains-with-tokens.json")

# ---------------------------------------------------------------------------
# 3. fetch native + ERC-20 balances, store a timestamped snapshot
# ---------------------------------------------------------------------------
loaders = [ethBalance.load0000r(atBlock=atBlock), *erc20Loaders]
accounts, errors = account0000r.loadAccountMetadata(loaders, accounts, chains)
snapshot = account0000r.writeJson(accounts)
print("balances saved to", snapshot)

# ---------------------------------------------------------------------------
# 4. fetch CURRENT prices for every symbol present
# ---------------------------------------------------------------------------
symbols = collectSymbols(accounts, chains)
priceLoaders = [
    CryptoCompare(),
    CoinGecko(symbol_overrides={
        "ETH": "ethereum", "WETH": "weth", "USDC": "usd-coin",
        "USDT": "tether", "DAI": "dai", "WBTC": "wrapped-bitcoin",
        "XDAI": "xdai", "GNO": "gnosis", "MATIC": "matic-network",
        "BNB": "binancecoin",
    }),
    Aliases({"XHOPR": "HOPR", "WXHOPR": "HOPR", "STETH": "ETH",
             "WETH": "ETH", "USDC.E": "USDC"}),
    Manual("data/assetPrices-manual.csv"),
]
prices = loadAssetPrices(symbols, int(time.time()), priceLoaders)
exportPrices(prices, "data/assetPrices-now.csv")

# ---------------------------------------------------------------------------
# 5. analyze: total + per-token + per-address (also writes 3 CSVs)
# ---------------------------------------------------------------------------
analyz0000r.portfolioValue(
    accounts, chains, atBlock=atBlock, assetPricesCsv="data/assetPrices-now.csv"
)
