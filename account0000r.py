"""Core steps of the pipeline: derive accounts, find blocks by timestamp, build one loader
per ERC-20 token, run loaders over accounts, and read/write the JSON files.

Account dicts look like
    {"address": "0x...", "index": 0, "mnemonic": "<description>", "profile": "personal",
     "chains": {"<chain name>": {"<loader name>": {...result...}}}}
Chain dicts are the entries of chains.json, optionally enriched with
    "metadata": {"blockNumberByTimestamp": {"timestamp": ..., "blockNumber": ...}}
and token entries enriched with "decimals".
"""

import json
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from hdwallet import BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet

from load0000rs import singleErc20
from rpc import build_web3, checksum
from utils import NonArchiveRpcError, retry, ts_to_utc


def readJson(path):
    with open(path) as f:
        return json.load(f)


def writeJson(data, fileName=None):
    """Write `data` as indented JSON, by default to data/accounts-<date>.json. Returns the path."""
    if fileName is None:
        fileName = "data/accounts-" + datetime.now().strftime("%Y-%m-%d--%H-%M-%S") + ".json"
    with open(fileName, "w") as f:
        json.dump(data, f, indent=2)
    return fileName


def accountsFromSecrets(secrets, accounts=None):
    """Derive BIP44 accounts from a list of secrets (see EXAMPLE-secrets.json) and append
    them to `accounts`, skipping addresses that are already present.

    Never log or store the mnemonics; only derived addresses leave this function.
    """
    accounts = [] if accounts is None else accounts
    known = {a["address"] for a in accounts}
    for s in secrets:
        hdPath = s.get("hdPath", "m/44'/60'/0'/0")
        numAccounts = int(s.get("numAccounts", 10))
        offset = int(s.get("accountOffset", 0))
        description = s.get("description", "")

        wallet = BIP44HDWallet(cryptocurrency=EthereumMainnet)
        wallet.from_mnemonic(mnemonic=s["mnemonic"], language="english",
                             passphrase=s.get("passphrase", ""))
        pathElements = hdPath.split("/")[1:]  # drop the leading "m"

        for index in range(offset, offset + numAccounts):
            wallet.clean_derivation()
            for elem in pathElements:
                wallet.from_index(int(elem.rstrip("'")), hardened=elem.endswith("'"))
            wallet.from_index(index, hardened=False)
            address = wallet.address()
            if address in known:
                continue
            known.add(address)
            accounts.append({"address": address, "index": index,
                             "mnemonic": description, "chains": {}})
    return accounts


def filterByProfile(accounts, profile):
    """Accounts whose "profile" equals `profile`, plus accounts without a profile.
    profile=None keeps everything."""
    if profile is None:
        return accounts
    kept = [a for a in accounts if a.get("profile", profile) == profile]
    if len(kept) < len(accounts):
        print(f"  profile={profile}: selected {len(kept)}/{len(accounts)} accounts")
    return kept


def mergeCachedChains(accounts, cachedAccounts):
    """Copy the "chains" results of cachedAccounts onto the accounts with the same
    address, so a re-run only fetches what is missing. Returns how many were merged."""
    cached = {a["address"].lower(): a.get("chains") for a in cachedAccounts}
    merged = 0
    for account in accounts:
        chains = cached.get(account["address"].lower())
        if chains:
            account["chains"] = chains
            merged += 1
    return merged


def _lastBlockBefore(web3, timestamp, low, high):
    """Binary search for the highest block number whose timestamp is <= `timestamp`."""
    found = None
    while low <= high:
        mid = (low + high) // 2
        if retry(web3.eth.get_block, mid)["timestamp"] <= timestamp:
            found, low = mid, mid + 1
        else:
            high = mid - 1
    return found


def getBlockNoFromTimestamp(chains, timestamp):
    """Store on every chain, under metadata.blockNumberByTimestamp, the last block mined
    at or before `timestamp`. Chains that cannot be reached are skipped with a message."""
    print(f"Looking for block at {ts_to_utc(timestamp)} across {len(chains)} chain(s):")
    for chain in chains:
        name = chain["name"]
        try:
            web3 = build_web3(chain)
            first = retry(web3.eth.get_block, 1)
            latest = retry(web3.eth.get_block, "latest")
            if not first.timestamp <= timestamp <= latest.timestamp:
                print(f"  [{name}] skipping: target is outside block 1 "
                      f"({ts_to_utc(first.timestamp)}) .. latest ({ts_to_utc(latest.timestamp)})")
                continue
            print(f"  [{name}] searching blocks 1..{latest.number}")
            blockNo = _lastBlockBefore(web3, timestamp, 1, latest.number)
            block = retry(web3.eth.get_block, blockNo)
            print(f"  [{name}] found block {blockNo} at {ts_to_utc(block.timestamp)}")
            chain.setdefault("metadata", {})["blockNumberByTimestamp"] = {
                "timestamp": timestamp, "blockNumber": blockNo}
        except Exception as e:
            print(f"  [{name}] skipping: {e}")
    return chains


def generateTokenLoad0000rs(chains, metaLoad0000r, loadChainData=True, atBlock=False):
    """One singleErc20 loader per token of every chain.

    With loadChainData=True each token's "decimals" is read from the chain and stored in
    the chain dict (write it to a file so later runs can pass loadChainData=False).
    Tokens without "decimals" are skipped. Returns (loaders, chains).
    """
    loaders = []
    total = sum(len(c.get("tokens", [])) for c in chains)
    done = 0
    start = time.time()
    for chain in chains:
        for token in chain.get("tokens", []):
            done += 1
            label = f"[{chain['name']}] {token.get('symbol', token.get('address', '?'))}"
            loader = singleErc20.load0000r(True, chain, token, metaLoad0000r, atBlock)
            if loadChainData:
                print(f"  {label}: loading token metadata ({done}/{total}, {time.time() - start:.0f}s elapsed)")
                try:
                    loader.loadTokenMetadata()
                except Exception as e:
                    print(f"  {label}: skipping, {e}")
                    continue
            if "decimals" not in token:
                print(f"  {label}: skipping, no decimals known (run with loadChainData=True)")
                continue
            loaders.append(loader)
    random.shuffle(loaders)  # spread consecutive requests across chains and endpoints
    return loaders, chains


def _printNonArchiveWarning(providers):
    if providers:
        print("\n" + "=" * 70)
        print("WARNING: these RPC providers are not archive nodes and were skipped for")
        print("historical queries. Use another endpoint for them in chains.json:")
        for p in sorted(providers):
            print(f"  {p}")
        print("=" * 70 + "\n")


def loadAccountMetadata(load0000rs, accounts, chains, max_workers=5):
    """Run every loader for every account on every chain and store the results in the
    account dicts. Returns (accounts, errors); errors is a list of message strings.

    Loader calls run in a thread pool; the accounts structure is only ever changed on
    the calling thread, so loaders must not touch it.
    """
    print(f"checking {len(accounts)} accounts on {len(chains)} chains:")
    tasks = []
    for account in accounts:
        account.setdefault("chains", {})
        address = checksum(account["address"])
        for loader in load0000rs:
            for chain in chains:
                account["chains"].setdefault(chain["name"], {})
                if loader.skipAnalysisIfEntryExists(account, chain):
                    print(f"skipping {loader.name()} for {address} on {chain['name']}, "
                          f"found entry from {loader.existingEntry(account, chain)['lastRun']}")
                else:
                    tasks.append((account, loader, chain, address))

    def store(account, loader, chain, entry):
        container = account["chains"][chain["name"]]
        if loader._metaLoad0000r is not None:
            container = container.setdefault(loader._metaLoad0000r.name(), {})
        container[loader.name()] = entry

    errors = []
    nonArchive = set()
    done = 0
    start = time.time()
    with ThreadPoolExecutor(max_workers=max(1, max_workers)) as pool:
        futures = {pool.submit(loader.analyze, address, chain): (account, loader, chain, address)
                   for account, loader, chain, address in tasks}
        for future in as_completed(futures):
            account, loader, chain, address = futures[future]
            try:
                entry = future.result()
            except NonArchiveRpcError as e:
                nonArchive.add(str(e))
                continue
            except Exception as e:
                errors.append(f"ERROR loading {loader.name()} for {address} on {chain['name']}: {e}")
                print(errors[-1])
                continue
            if entry is not None:
                store(account, loader, chain, entry)
            done += 1
            elapsed = time.time() - start
            print(f"progress: {done}/{len(tasks)} in {elapsed:.0f}s, ~{elapsed / done * (len(tasks) - done):.0f}s "
                  f"remaining ({address} on {chain['name']}, {loader.name()})")

    _printNonArchiveWarning(nonArchive)
    if errors:
        print(f"{len(errors)} errors:")
        print(*errors, sep="\n")
    return accounts, errors
