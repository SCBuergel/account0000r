# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
pyenv local 3.11
pip install -r requirements.txt
```

Required config files (not in repo):
- `secrets.json` — list of mnemonics/passphrases (see `EXAMPLE-secrets.json`)
- `chains.json` — chain RPC endpoints and token lists (see `data/chains-sample.json`)

## Running

```bash
python runn0000r.py    # main entry point with usage snippets
python rpc_test.py     # RPC performance benchmarking
```

## Architecture

The tool follows a **load → store → analyze** pipeline:

1. **Generate accounts** — `account0000r.accountsFromSecrets(secrets_file)` derives BIP44 HD wallet addresses from `secrets.json`, or accounts can be assembled manually as a JSON list.
2. **Load metadata** — `account0000r.loadAccountMetadata(loaders, accounts, chains)` runs each `load0000r` against each account on each chain. Results are stored under `account["chains"][chainName][loaderName]`.
3. **Store results** — `account0000r.writeJson(accounts)` saves to a timestamped file in `data/`.
4. **Analyze** — functions in `analyz0000r.py` print/display results.

### Loaders (`load0000rs/`)

All loaders inherit from `baseLoad0000r` (`load0000rs/base.py`). Key methods to implement:
- `name()` — unique string key used as the field name in output JSON
- `version()` — version string stored alongside results
- `analyze(w3, account, chain)` — performs the actual data fetch; `w3` is a `web3.Web3` instance

Loader instances are passed as a list to `loadAccountMetadata`. The base class supports:
- `skipIfEntryExists` — skip re-querying if data already loaded
- Meta-loaders (e.g. `metaLoad0000rErc20`) that generate child loaders dynamically

Built-in loaders: `ethBalance`, `nonce`, `erc20Balance`, `erc20BalanceAtBlock`, `singleErc20`, `airdropOpApi`, `airdropHopApi`, `airdropHopJson`, `airdropDymApi`.

### Token loaders

Before calling `loadAccountMetadata` with ERC20 loaders, generate them via:
```python
erc20Loaders, chains = account0000r.generateTokenLoad0000rs(chains, metaErc20, loadChainData=False)
```

### Utilities

- `utils._exponential_backoff(fn, ...)` — retry wrapper for RPC calls
- `getPrices.py` — fetches token prices from CoinGecko

### Data format

Account objects are plain dicts:
```json
{
  "address": "0x...",
  "index": 0,
  "mnemonic": "label",
  "chains": {
    "Ethereum Main Net": {
      "ethBalance": { "value": "...", "version": "...", "lastRun": "..." }
    }
  }
}
```
