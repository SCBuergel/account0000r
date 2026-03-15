# account0000r - extendable EVM account overview

account0000r lets you check EVM accounts accross chains. It keeps a local record in a JSON file and is aimed at being easily extendable. It helps you answer questions such as:

> On which chain did I use this account?

> Which of my 100 accounts has a balance > 0 on any chain?

> I backed up my mnemonic, but where are the accounts and which of them did I ever use?

> Do I have any unclaimed [ENTER PROJECT NAME] airdrops for any of my 100 accounts?

![The account0000r Wojak meme](https://github.com/SCBuergel/account0000r/blob/main/TheAccount0000r.png?raw=true "The account0000r")



## Prerequisites
account0000r expects a local python installation. I recommend [`pyenv`](https://github.com/pyenv/pyenv-installer) for that and have [automated](https://github.com/SCBuergel/SEQS) the installation of that setup for my QubesOS.

Install Python 3.11 and the required packages via
```
pyenv local 3.11
pip install -r requirements.txt
```



## Usage

account0000r comprises a set of Python tools to derive accounts, load metadata of accounts and analyze them. 
See the `runn0000r.py` script for usage examples.

The main features are the `load0000r` classes which load metadata of accounts and `analyz0000r` functions which print analysis results of those account metadata.
Both `load0000r` classes and `analyz0000r` functions are easily extendable as outlined below.

The account0000r Python package is built for managing accounts in separate steps:

### 1. `account0000r.accountsFromSecrets`
Returns a list of BIP44 HD wallet Ethereum accounts with metadata from a mnemonic & passphrase setting file (see more information on settings files below).
Only load mnemonics if you know what you are doing and on a computer that you fully trust. Otherwise all funds association with these mnemonics will be at risk.
Alternatively, you can assemble the accounts.json file manually (see below for more information on how that file is structured).

### 2. `account0000r.writeJson`
Stores the list of accounts and metadata.
This file can be read at a later time for loading additional metadata of each account or add more accounts that are derived from mnemonic and passphrase

### 3. Read account data from file
Since account metadata files stored as JSON, they can be loaded via
```
import json
accounts = json.load(open("accounts.json")) 
```

### 4. `account0000r.loadAccountMetadata`
Loads account data from a set of EVM chains.
Simple examples that are included already now are balances, nonces of accounts but account0000r's extendable nature makes this step easily adjustable to load token balances, pending airdrop claims or other highly custom properties by writing your own `load0000r` (see below for more details).
The chains from which metadata is loaded are specified in the `chains.json` file (see more info on settings files below).

### 5. Run analyz0000r
After loading account metadata via a `load0000r`, the results are recorded in the `accounts` list and can be analyzed (and typically printed to the console output) via a corresponding `analyz0000r` function.
account0000r makes it easy to write your own `analyz0000r` function (see below for more details).



## Write your own `load0000r`
You can easily extend the capabilities of account0000r by writing your own `load0000r` class which loads additional account-specific metadata.
The specific data is loaded via `load0000r` classes (locaded in the `load0000r` folder) that are all derived from an abstract `baseLoad0000r` class.
Instances of each `load0000r` are then passed as a list to the `account0000r.loadAccountMetadata` function.
When writing your own `load0000r`, you can follow the examples in the `load0000rs` folder, `import` it in the `runn0000r.py` file and pass an instance of it to the list argument of the `account0000r.loadAccountMetadata` function.



## Write your own `analyz0000r`
Similar as with writing your own `load0000r`, you can easily write a correponding `analyz0000r` function to e.g. display results and write them to the console.
While you can write the analysis functions however you please, it is recommended to add them to the `analyz0000r.py` file and `import` the function in the `runn0000r.py` file and also call it from there, just like for the provided functions.



## File and folder structure
```
.
├── data - contains JSON output files with account metadata
│   ├── accountsBlank.json                 - blank accounts example without metadata, use this as a basis if you do not want to use the mnemonic account import
│   └── accounts-2022-07-09--22-20-10.json - example of an account metadata file
├── load0000rs
│   ├── base.py       - contains the base class `baseLoad0000r`
│   ├── ethBalance.py - native balance loader
│   └── nonce.py      - account nonce loader
├── priceLoad0000rs
│   ├── __init__.py         - orchestrator: `loadAssetPrices`, `collectSymbols`, `eoyTimestamp`
│   ├── base.py             - abstract `basePriceLoad0000r` class
│   ├── cryptocompare.py    - primary price source (CryptoCompare histoday API, no key required)
│   ├── coingecko.py        - fallback price source (CoinGecko history API)
│   └── manual.py           - last-resort override from a hand-maintained CSV file
├── account0000r.py - the main account0000r module with the main functions
├── analyz0000r.py - contains the functions which are used inside the `runn0000r.py` file to print analysis results of account metadata.
├── chains.json - the settings file of the chains from which to load metadata
├── EXAMPLE-secrets.json - rename this to `secrets.json` and customize. Only load mnemonics if you know what you are doing and on a computer that you fully trust. Otherwise all funds association with these mnemonics will be at risk.
├── README.md - this README file
└── runn0000r.py - an example file with snippets to initialize accounts, load metadata and run simple analysis on the acccounts metadata object
```



## Account metadata files
A list of accounts can be created via `account0000r.accountsFromSecrets` or (e.g. if you rightly do not feel like it is a smart idea to expose your mnemonic to this tool) you compile this file manually following the structure below.
```
[
  {
    "address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    "index": 0,
    "mnemonic": "Vitalik"
  },
  {
    "address": "0x1Db3439a222C519ab44bb1144fC28167b4Fa6EE6",
    "index": 1,
    "mnemonic": "Vitalik"
  }
]
```
The `mnemonic` and `index` field allows `analyz0000r`s to group the output of accounts for getting a better overview when handling a large number of addresses which are derived from various mnemonics.

After running any of the `load0000r`s, the new file 
(all files are appended with a date, so you don't have to worry about files getting overwritten)
will contain an additional `chains` field for each address.
For each chain that is found in the `chains.json` file you will then find results of the `load0000r`s.
You can see the example output file in the `data` folder for details.



## Settings files
Requires a `secrets.json` file in the root directory which contains a list of mnemonics and passphrases, as follows:
```
[
  {
    "mnemonic": "zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo wrong",
    "description": "plain testvector mnemonic"
  },
  {
    "mnemonic": "zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo wrong",
    "passphrase": "rekt",
    "hdPath": "m/44'/60'/0'",
    "numAccounts": 20,
    "accountOffset": 1000,
    "description": "testvector mnemonic with password"
  }
]
```
The following are optional fields with indicated default values:
```
"passphrase" (default: "")
"hdPath" (default: "m/44'/60'/0'/0")
"numAccounts" (default: 10)
"accountOffset" (default: 0)
"description" (default: "")
```

It also requires a `chains.json` file in the root directory with a list of chain names, RPC provider, chain id, native asset name and list of tokens (can be an empty list) on that chain that account0000r can load:
```
[
  {
    "name": "Ethereum Main Net",
    "api": "https://eth.llamarpc.com",
    "id": 1,
    "nativeAsset": "ETH",
    "tokens": [
      {
        "symbol": "WETH",
        "address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
      },
      {
        "symbol": "DAI",
        "address": "0x6B175474E89094C44Da98b954EedeAC495271d0F"
      }
    ]
  },
  {
    "name": "Gnosis Chain",
    "api": "https://rpc.ankr.com/gnosis",
    "id": 100,
    "nativeAsset": "xDAI",
    "tokens": []
  }
]
```

## List of load0000rs
load0000rs are loading account metadata. Often times (but not necessarily) this happens via RPC calls such as getting a native coin or ERC20 token balance. Several load0000rs currently exist and can be easily extended by writing your own (see above).

### `nonce` load0000r
Loads the nonce at the current block.

## List of analyz0000rs
analyz0000rs are analyzing account metadata. Often times the results are displayed in the terminal or written to a file. Several analyz0000rs currently exist and can be easily extended by writing your own (see above).

### `tabulateAllAccounts`
Prints a table of all accounts

### `tabulateNonZeroNonce`
Prints a binary table of accounts with non-zero nonces, sorted by mnemonic and index
```
╒═════════╤════════╤════════╤════════╤════════╕
│   index │ mnem 1 │ work   │ fam    │ aping  │
│         │        │ stuff  │        │ 2021   │
╞═════════╪════════╪════════╪════════╪════════╡
│       0 │ X      │ X      │ X      │ X      │
├─────────┼────────┼────────┼────────┼────────┤
│       1 │ X      │ X      │        │ X      │
├─────────┼────────┼────────┼────────┼────────┤
│       2 │        │ X      │ X      │ X      │
├─────────┼────────┼────────┼────────┼────────┤
│       3 │        │        │ X      │ X      │
├─────────┼────────┼────────┼────────┼────────┤
│       4 │        │        │ X      │ X      │
├─────────┼────────┼────────┼────────┼────────┤
│       5 │        │        │        │ X      │
├─────────┼────────┼────────┼────────┼────────┤
│       6 │        │        │ X      │ X      │
├─────────┼────────┼────────┼────────┼────────┤
│       7 │        │        │ X      │ X      │
├─────────┼────────┼────────┼────────┼────────┤
│       8 │        │        │        │ X      │
├─────────┼────────┼────────┼────────┼────────┤
│       9 │        │        │        │ X      │
╘═════════╧════════╧════════╧════════╧════════╛
```

## EOY asset prices

The `priceLoad0000rs` module fetches end-of-year (or any-date) closing prices in USD for a list of asset symbols.
It mirrors the `load0000rs` pattern: a base class defines the interface, concrete implementations provide the data, and an orchestrator function ties them together.

### How it works

1. **Collect symbols** — `collectSymbols(accounts, chains)` scans your loaded account data and chain definitions to build the full list of asset tickers that appear with a non-zero balance (native coins + ERC-20 tokens). No manual list maintenance needed.
2. **Pick a timestamp** — `eoyTimestamp(year)` returns the Unix timestamp for midnight UTC on Jan 1 of `year + 1`, which is the conventional EOY snapshot point. You can also supply any Unix timestamp directly.
3. **Load prices** — `loadAssetPrices(symbols, timestamp, loaders)` tries each loader in order. The first loader that returns a price for a symbol wins; remaining symbols are passed to the next loader. Any symbol with no price found is reported as a warning.
4. **Export** — the returned `dict[symbol → price]` can be written to a CSV with `getPrices.export_prices()` and consumed directly by `analyz0000r.portfolioValue()`.

### Price loaders

| Loader | Source | Notes |
|--------|--------|-------|
| `cryptocompare.CryptoCompare` | [CryptoCompare histoday API](https://min-api.cryptocompare.com) | No API key needed. Primary source for most assets. Returns the daily close at the given timestamp. |
| `coingecko.CoinGecko` | [CoinGecko history API](https://www.coingecko.com/en/api) | No API key for public tier. Fetches the full coin list once to resolve symbol→id mapping. Pass `symbol_overrides={"WETH": "weth"}` to resolve ambiguous tickers. |
| `aliases.Aliases` | Derived/wrapped tokens | Maps tokens to their underlying asset (e.g. `xHOPR → HOPR`, `stkAAVE → AAVE`, `rETH → ETH`). Must be placed **after** the loaders that resolve the underlyings. |
| `manual.Manual` | Local CSV file | Reads the same `Asset,Price` CSV format that `portfolioValue()` consumes. Use for illiquid or obscure tokens (SAI, STAKE, FOAM, …) that APIs no longer cover. Silent no-op if the file is absent. |

### Example

```python
from priceLoad0000rs import loadAssetPrices, collectSymbols, eoyTimestamp, exportPrices
from priceLoad0000rs.cryptocompare import load0000r as CryptoCompare
from priceLoad0000rs.coingecko import load0000r as CoinGecko
from priceLoad0000rs.aliases import load0000r as Aliases
from priceLoad0000rs.manual import load0000r as Manual

# accounts and chains must already be loaded
loaders = [
    CryptoCompare(),
    CoinGecko(),
    Aliases({"XHOPR": "HOPR", "WXHOPR": "HOPR", "STKAAVE": "AAVE", "RETH": "ETH", "STETH": "ETH", "WETH": "ETH"}),
    Manual("data/assetPrices-manual.csv"),
]
symbols = collectSymbols(accounts, chains)   # e.g. ["ETH", "GNO", "USDC", "xDAI"]
prices  = loadAssetPrices(symbols, eoyTimestamp(2024), loaders)
exportPrices(prices, "data/assetPrices-EOY2024.csv")

# now use it
analyz0000r.portfolioValue(accounts, chains, assetPricesCsv="data/assetPrices-EOY2024.csv")
```

Any symbols that no loader could resolve are printed as a warning. Add them to your manual CSV and re-run.

### Writing your own price loader

Subclass `basePriceLoad0000r` from `priceLoad0000rs/base.py` and implement three methods:

```python
from priceLoad0000rs.base import basePriceLoad0000r

class load0000r(basePriceLoad0000r):
    def name(self) -> str:    return "mysource"
    def version(self) -> str: return "0.0.1"
    def fetchPrice(self, symbol: str, timestamp: int) -> float | None:
        # fetch and return closing USD price, or None if unavailable
        ...
```

Pass an instance as part of the `loaders` list to `loadAssetPrices`.



## Utils
Some utils do not fit into a generalized structure yet and are described here

## `account0000r.generateTokenLoad0000rs`
Is used before the actual `loadAccountMetadata` step to e.g. generate the erc20Load0000rs and erc20 token data (decimals, name, symbol).
It is typically called like this:
```
erc20Load0000rs, chains = account0000r.generateTokenLoad0000rs(chains, metaErc20, loadChainData=False)
```
the last parameter can be set to False to not actually load any on-chain data (e.g. if the chains object already contains everything that is needed and only the erc20Load0000rs need to be regenerated).

This step is preparing a list of `singleErc20AtBlock` load0000rs for each token that is referenced in the chain.
