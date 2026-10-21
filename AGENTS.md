# AGENTS.md

Guidance for AI agents (and humans) changing this repository. Read README.md first for
what the tool does; this file covers how the code is organised and what must stay true.

## Map

```
accounting.py        CLI: end-of-year pipeline, steps 0-6, one output file per step
networth_now.py      CLI: current net worth, reuses accounting's helpers and file names
account0000r.py      core: derive accounts, find block by timestamp, build token loaders,
                     run loaders over accounts (thread pool), read/write JSON
analyz0000r.py       tables and the portfolio valuation (pandas)
rpc.py               build_web3(chain): Web3 with failover across a chain's endpoints
rpc_test.py          CLI: benchmark the endpoints in a chains file
utils.py             retry(), NonArchiveRpcError, deep_get, ts_to_utc
load0000rs/          one class per fact fetched per account and chain (base.py has the contract)
priceLoad0000rs/     one class per price source, plus the orchestration in __init__.py
data/                user data; only the samples and chains.json are tracked
tests/, conftest.py  pytest suite, no network
```

Setup: Python 3.11, `pip install -r requirements.txt`, then `pytest`. Run everything from
the repository root; all paths in the code are relative to it.

## Conventions

- Module and function names are camelCase with the `0000r` suffix for the tool's own
  concepts (`load0000r`, `analyz0000r`). Keep that style; do not rename for its own sake.
- Every loader module exposes a class named `load0000r` and, when other code needs the
  result key, a module constant `NAME`. Import those constants instead of repeating the
  strings (`ethBalance.NAME`, `metaLoad0000rErc20.NAME`).
- The two CLIs own their file names (`data/accounts-<year>.json`, `data/*-now.*`). Keep
  EOY data and current data in separate files: both are stored under the same loader
  keys except for the ` atBlock` suffix, and `listAllNonDustBalances` tells them apart only
  by that suffix.
- Loader results always start from `createEmptyAccountEntry()` so every stored entry has
  `version` and `lastRun`. Re-runs rely on `lastRun` existing.
- Print progress with plain `print`; there is no logging framework.
- Add a test for every behaviour change. Tests must not touch the network: monkeypatch
  `HTTPProvider.make_request` or `requests.get` as the existing tests do.

## Invariants

- Mnemonics never leave `accountsFromSecrets`: do not print, store or pass them on.
  `secrets.json` and `accounts-*.json` are gitignored; keep them so.
- `loadAccountMetadata` changes the accounts structure only on the calling thread.
  `analyze()` runs in worker threads and must only return a value.
- Always connect through `rpc.build_web3(chain)`. It injects the POA middleware and the
  per-chain failover cursor; a bare `Web3(HTTPProvider(...))` would lose both.
- Wrap RPC calls in `utils.retry`. It turns "missing trie node" into `NonArchiveRpcError`,
  which `loadAccountMetadata` collects into one warning instead of retrying.
- A step of `accounting.py` reads only files written by earlier steps and writes only its
  own file, so any step can be re-run alone.

## Gotchas

- web3 6.2 imports `pkg_resources`, so `setuptools<70` is pinned. web3 7 renamed the POA
  middleware; upgrading means touching `rpc.py`.
- web3 6 ships a broken pytest plugin; `pytest.ini` disables it (`-p no:pytest_ethereum`).
- Public RPC endpoints come and go. An endpoint that answers every request with a
  JSON-RPC error (for example Ankr without a key) is rotated away like a dead one.
- CryptoCompare requires `CRYPTOCOMPARE_API_KEY`; CoinGecko's public API refuses dates
  older than 365 days. Both are documented in README.md; keep the docs and the loaders in
  step when the APIs change again.
- MKR and SAI return their symbol as bytes32; `singleErc20.loadTokenMetadata` treats a
  failing `symbol()` call as "unknown" rather than an error.

## Working on this repository

- Keep it small. Prefer deleting a feature nobody can run (dead API, missing data file)
  over keeping it half-working; the git history has the old code.
- Update README.md in the same change when behaviour, file names or options change.
- Verify RPC-facing changes with a short live script against one chain and one public
  address (Vitalik's `0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045` works well).
