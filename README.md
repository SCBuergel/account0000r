# account0000r

account0000r answers questions about many EVM accounts at once, across many chains:

> Which of my 100 accounts has a balance on any chain?

> What was my whole portfolio worth at the end of last year, for my tax return?

> I backed up a mnemonic, but which of its accounts did I ever use?

It derives the accounts from your mnemonics (or takes a list of addresses), asks
public RPC endpoints for balances, fetches prices, and prints the portfolio as tables.
Everything it learns is kept in JSON and CSV files under `data/`, so a re-run only
fetches what is still missing.

![The account0000r Wojak meme](https://github.com/SCBuergel/account0000r/blob/main/TheAccount0000r.png?raw=true "The account0000r")

## How it works

Three kinds of objects flow through the tool:

- **Accounts**: a list of `{"address", "index", "mnemonic"}` records, either derived
  from `secrets.json` or written by hand. `mnemonic` holds a label, never the words.
- **Chains**: `data/chains.json`, one entry per chain with its RPC endpoints, native
  asset and the ERC-20 tokens to look at.
- **Loaders** (`load0000rs/`): small classes that fetch one fact for one account on one
  chain, such as the native balance or one token balance. The tool runs every loader for
  every account on every chain and stores each result inside the account record, under
  the chain name and the loader name. Writing a new loader is the way to extend the tool.

The stored account records are then priced (`priceLoad0000rs/`) and summarised
(`analyz0000r.py`). Two commands drive all of this:

| Command | Question it answers | Balances as of |
|---|---|---|
| `python accounting.py <year> <steps>` | What was the portfolio worth at the end of `<year>`? | the last block of that year |
| `python networth_now.py` | What is the portfolio worth right now? | the latest block |

## Install

Python 3.11 is required (pandas 2.0 has no wheels for newer versions). With
[pyenv](https://github.com/pyenv/pyenv-installer):

```
pyenv install 3.11
pyenv local 3.11
pip install -r requirements.txt
```

## Configure

### secrets.json: mnemonics (optional)

Only needed if the tool should derive accounts for you. **Anyone who reads this file
controls all funds behind the mnemonics.** Create it only on a machine you fully trust,
and never commit it (the `.gitignore` excludes it). Copy `EXAMPLE-secrets.json` and
edit; every entry supports:

```
"mnemonic"       required
"passphrase"     default ""
"hdPath"         default "m/44'/60'/0'/0"
"numAccounts"    default 10      how many accounts to derive
"accountOffset"  default 0       index of the first account
"description"    default ""      label shown in the output as "mnemonic"
```

If you would rather not expose mnemonics, skip `secrets.json` and write the account list
yourself, see [Account files](#account-files).

### data/chains.json: chains and tokens

One entry per chain. `api` is one URL or a list; with a list the tool switches to the
next endpoint when one fails. `tokens` lists the ERC-20 tokens to query on that chain;
their decimals are read from the chain, you only give symbol and address.

```json
[
  {
    "name": "Ethereum Main Net",
    "api": ["https://ethereum-rpc.publicnode.com", "https://eth.drpc.org"],
    "id": 1,
    "nativeAsset": "ETH",
    "tokens": [
      {"symbol": "DAI", "address": "0x6B175474E89094C44Da98b954EedeAC495271d0F"}
    ]
  },
  {"name": "Gnosis Chain", "api": "https://rpc.gnosischain.com", "id": 100, "nativeAsset": "xDAI"}
]
```

End-of-year balances need **archive** endpoints (ones that can answer "balance at block
N" for old N). `python accounting.py 2024 0` tells you which of your endpoints qualify,
and `python rpc_test.py` measures success rate and latency of every endpoint listed.

### data/assetPrices-manual.csv: prices the APIs do not know

An `Asset,Price` CSV in USD for tokens no price API covers (SAI, STAKE, ...). It is the
last price source tried, so it also overrides nothing.

### Price API keys (optional)

Prices come from CryptoCompare and CoinGecko. Set these environment variables if needed:

- `CRYPTOCOMPARE_API_KEY`: CryptoCompare requires a key since 2025 (free at
  https://developers.coindesk.com/). Without it the source is skipped.
- `COINGECKO_API_KEY`: a CoinGecko demo key raises the rate limit. With or without a key
  the public API only serves dates within the last 365 days, so run an end-of-year
  valuation early in the following year, or use CryptoCompare or the manual CSV.

### Profiles

An account may carry `"profile": "personal"` or `"corporate"` or any other label.
Balances are always loaded for all accounts; the `--profile` option of both commands
limits the analysis to one profile. Accounts without a profile belong to every profile.

## End-of-year accounting

```
python accounting.py 2024 1-6                    full run
python accounting.py 2024 0                      only check the RPC endpoints
python accounting.py 2024 5,6                    prices and analysis again
python accounting.py 2024 6 --profile corporate  analysis of the "corporate" accounts
```

Each step writes a file that the next steps read, so you can re-run any step alone:

| Step | Does | Writes |
|---|---|---|
| 0 | checks that every chain's endpoint answers and is an archive node | nothing |
| 1 | derives accounts from `secrets.json` | `data/accounts-blank.json` |
| 2 | finds the last block of the year on every chain | `data/chains-2024-blocks.json` |
| 3 | reads token decimals from the chains | `data/chains-2024-tokens.json` |
| 4 | loads every account's balances at that block (slow) | `data/accounts-2024.json` |
| 5 | fetches prices for every asset held | `data/assetPrices-2024.csv` |
| 6 | prints the portfolio | `data/account_balances.csv`, `asset_values.csv`, `address_values.csv` |

Step 4 keeps balances already in `data/accounts-2024.json` and only fetches the rest, so
a run that was interrupted or hit a dead endpoint can simply be started again. Likewise
step 5 keeps prices already in the CSV. Delete the file to fetch everything again.

If an endpoint is not an archive node, step 4 skips that chain and prints a warning
listing the endpoint; put an archive endpoint in `chains.json` and re-run step 4. Assets
without a price are listed at the end of step 6 and excluded from the total; add them to
the manual CSV and re-run steps 5 and 6.

## Current net worth

```
python networth_now.py                 reuse balances and prices from the last run
python networth_now.py --refresh       fetch everything again
```

Needs `data/accounts-blank.json` (from accounting step 1, or hand-written) and
`data/chains.json`. It keeps its own files, `data/accounts-now.json`,
`data/chains-now-tokens.json` and `data/assetPrices-now.csv`, and reuses them on the
next run. Reused balances and prices are as old as the run that fetched them.

## Account files

A hand-written account list has the shape of `data/accounts-blank-sample.json`:

```json
[
  {"address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045", "index": 0, "mnemonic": "Vitalik"},
  {"address": "0x1Db3439a222C519ab44bb1144fC28167b4Fa6EE6", "index": 1, "mnemonic": "Vitalik", "profile": "corporate"}
]
```

`mnemonic` and `index` group the output when you have many accounts from several
mnemonics. After loading, each account gains a `chains` field with one entry per chain
and, inside it, one entry per loader:

```json
"chains": {
  "Ethereum Main Net": {
    "ETH balance at block": {"version": "0.0.1", "lastRun": "2025-01-02--10-00-00", "nativeBalance": 1.5},
    "ERC20 balances": {
      "Single ERC20 balance DAI on Ethereum Main Net atBlock": {
        "version": "0.0.1", "lastRun": "2025-01-02--10-00-00",
        "erc20Balance": {"symbol": "DAI", "balance": 100.0}
      }
    }
  }
}
```

## Extending

**A new loader** fetches another fact per account and chain. Subclass
`load0000rs/base.py` and implement `name()`, `version()` and `analyze(account, chain)`;
`load0000rs/nonce.py` is the shortest example. `analyze` receives the checksummed address
and the chain dict, connects with `rpc.build_web3(chain)`, wraps calls in `utils.retry`,
and returns `self.createEmptyAccountEntry()` with the result added. Pass an instance to
`account0000r.loadAccountMetadata` from a small script:

```python
import account0000r, analyz0000r
from load0000rs import nonce

accounts = account0000r.readJson("data/accounts-blank.json")
chains = account0000r.readJson("data/chains.json")
accounts, errors = account0000r.loadAccountMetadata([nonce.load0000r()], accounts, chains)
account0000r.writeJson(accounts, "data/accounts-nonces.json")
analyz0000r.tabulateNonZeroNonce(accounts)   # grid of the accounts that ever sent a transaction
```

**A new price source** subclasses `priceLoad0000rs/base.py` and implements
`fetchPrice(symbol, timestamp)` returning a USD price or `None`;
`priceLoad0000rs/manual.py` is the shortest example. Sources are tried in order; the
first price found wins (`priceLoad0000rs.defaultPriceLoaders` has the default order).

**A new analysis** is a function over the account list; see `analyz0000r.py`.

## Tests

```
pytest
```

The tests need no network. They cover account derivation (against the test-vector
mnemonics in `EXAMPLE-secrets.json`), the loader runner, endpoint failover, the price
pipeline and the portfolio tables.
