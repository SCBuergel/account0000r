"""Analysis functions: turn loaded account data into tables and a portfolio valuation."""

import os

import pandas as pd
from tabulate import tabulate

from load0000rs import ethBalance, metaLoad0000rErc20, nonce
from utils import deep_get


def printBinaryTable(data):
    """Print a grid with one column per mnemonic and one row per account index, marking
    every (mnemonic, index) pair in `data` with an X."""
    if not data:
        print("  (no accounts match; is the loader data loaded?)")
        return
    mnemonics = sorted({m for m, _ in data})
    indices = [int(i) for _, i in data]
    lo, hi = min(indices), max(indices)
    rows = [[index] + [" "] * len(mnemonics) for index in range(lo, hi + 1)]
    for mnemonic, index in data:
        rows[int(index) - lo][mnemonics.index(mnemonic) + 1] = "X"
    headers = ["index"] + [m.replace(" ", "\n") for m in mnemonics]
    print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))


def _warnIfLoaderMissing(accounts, loaderName):
    if not any(loaderName in c for a in accounts for c in a.get("chains", {}).values()):
        print(f"WARNING: no account has '{loaderName}' data. Run that loader first.")


def listAccountsNonZero(accounts, load0000r=ethBalance.NAME, dust=0, printCsv=False):
    """Print every (account, chain) whose native balance is above `dust`."""
    print(f"Accounts with > {dust} {load0000r} per chain")
    for a in accounts:
        for chainName, chainData in a["chains"].items():
            balance = deep_get(chainData, load0000r, "nativeBalance", default=0)
            if balance > dust:
                if printCsv:
                    print(f"{a['address']}, {chainName}, {balance},")
                else:
                    print(f"{a['address']} ({a['mnemonic']}, index {a['index']}): {balance} on {chainName}")


def tableAccountsNonZeroBalance(accounts, load0000r=ethBalance.NAME, dust=0):
    """Grid of accounts whose native balance summed over all chains is above `dust`."""
    print(f"Accounts with > {dust} {load0000r} summed over chains")
    _warnIfLoaderMissing(accounts, load0000r)
    printBinaryTable([
        (a["mnemonic"], a["index"]) for a in accounts
        if sum(deep_get(c, load0000r, "nativeBalance", default=0) for c in a["chains"].values()) > dust
    ])


def tabulateNonZeroNonce(accounts):
    """Grid of accounts that sent at least one transaction on any chain."""
    _warnIfLoaderMissing(accounts, nonce.NAME)
    printBinaryTable([
        (a["mnemonic"], a["index"]) for a in accounts
        if any(deep_get(c, nonce.NAME, "nonce", default=0) > 0 for c in a["chains"].values())
    ])


def listAllNonDustBalances(accounts, chains, dust=0, atBlock=False):
    """DataFrame with columns Address, Chain, Balance, Asset: every native and ERC-20
    balance above `dust`. atBlock selects the end-of-year loader results."""
    nativeLoader = ethBalance.NAME_AT_BLOCK if atBlock else ethBalance.NAME
    nativeAsset = {c["name"]: c.get("nativeAsset", "?") for c in chains}
    rows, missing = [], []
    for a in accounts:
        for chainName, chainData in a.get("chains", {}).items():
            balance = deep_get(chainData, nativeLoader, "nativeBalance")
            if balance is None:
                missing.append(f"  {a['address']} on {chainName}")
            elif balance > dust:
                rows.append((a["address"], chainName, balance, nativeAsset.get(chainName, "?")))
            for loaderName, entry in chainData.get(metaLoad0000rErc20.NAME, {}).items():
                if loaderName.endswith(" atBlock") != atBlock:
                    continue
                token = entry.get("erc20Balance", {})
                if token.get("balance", 0) > dust:
                    rows.append((a["address"], chainName, token["balance"], token["symbol"]))
    if missing:
        print(f"WARNING: '{nativeLoader}' not loaded for {len(missing)} account/chain pairs (skipped):")
        print("\n".join(missing))
    return pd.DataFrame(rows, columns=["Address", "Chain", "Balance", "Asset"])


def _describeAddresses(byAddress, accounts):
    """The per-address value Series as a DataFrame with the account's Mnemonic (its
    description), Index and, when any account has one, Use and Profile, in front of Value."""
    info = {a["address"]: a for a in accounts}
    table = byAddress.rename("Value").to_frame()
    columns = [("Mnemonic", "mnemonic"), ("Index", "index"), ("Use", "use"), ("Profile", "profile")]
    for column, field in columns:
        values = [info.get(addr, {}).get(field, "") for addr in table.index]
        if field in ("mnemonic", "index") or any(v != "" for v in values):
            table.insert(len(table.columns) - 1, column, values)
    return table


def readPrices(assetPricesCsv):
    """Asset -> USD price Series from an Asset,Price CSV; empty if the file is missing."""
    if not os.path.exists(assetPricesCsv):
        return pd.Series(dtype=float)
    prices = pd.read_csv(assetPricesCsv, skipinitialspace=True)
    prices["Asset"] = prices["Asset"].str.strip().str.upper()
    return prices.drop_duplicates("Asset").set_index("Asset")["Price"]


def portfolioValue(accounts, chains, atBlock=False, assetPricesCsv="data/assetPrices.csv",
                   storeCsv=True, outputDir="data"):
    """Print every balance with its USD value, totals per asset and per address, and the
    portfolio total. Assets without a price are listed as a warning. With storeCsv the
    three tables are also written to <outputDir>/{account_balances,asset_values,address_values}.csv.
    Returns the balances DataFrame."""
    prices = readPrices(assetPricesCsv)
    balances = listAllNonDustBalances(accounts, chains, atBlock=atBlock)
    balances["Asset"] = balances["Asset"].str.upper()
    balances["Price"] = balances["Asset"].map(prices)
    balances["Value"] = balances["Balance"] * balances["Price"]

    byAddress = balances.groupby("Address")["Value"].sum().sort_values(ascending=False)
    balances["_total"] = balances["Address"].map(byAddress)
    balances = (balances.sort_values(["_total", "Address", "Value"], ascending=[False, True, False])
                .drop(columns="_total").reset_index(drop=True))

    pretty = balances.copy()
    pretty["Balance"] = pretty["Balance"].map("{:,}".format)
    pretty["Price"] = pretty["Price"].map(lambda p: f"${p:,.4f}" if pd.notna(p) else "(no price)")
    pretty["Value"] = pretty["Value"].map(lambda v: f"${v:,.2f}" if pd.notna(v) else "?")
    print("All accounts and balances:")
    print(pretty.to_string(index=False))

    byAsset = balances.groupby("Asset").agg(Balance=("Balance", "sum"), Price=("Price", "first"),
                                            Value=("Value", "sum"))
    # list configured assets that no account holds, so a zero is visible rather than absent
    configured = {c["nativeAsset"].upper() for c in chains if c.get("nativeAsset")}
    configured |= {t["symbol"].upper() for c in chains for t in c.get("tokens", []) if t.get("symbol")}
    for asset in sorted(configured - set(byAsset.index)):
        byAsset.loc[asset] = [0.0, prices.get(asset), 0.0]
    byAsset = byAsset.sort_values("Value", ascending=False)
    print("\nAssets by value:")
    print(byAsset.assign(Balance=byAsset["Balance"].map("{:,.2f}".format),
                         Value=byAsset["Value"].map("${:,.2f}".format)).to_string())

    byAddress = _describeAddresses(byAddress, accounts)
    print("\nAccounts by total value:")
    print(byAddress.assign(Value=byAddress["Value"].map("${:,.2f}".format)).to_string())

    print(f"\nTotal portfolio value (priced assets only): ${balances['Value'].sum():,.2f}")
    unpriced = sorted(balances.loc[balances["Price"].isna(), "Asset"].unique())
    if unpriced:
        print(f"WARNING: no price for {len(unpriced)} asset(s), the total is incomplete: {unpriced}")

    if storeCsv:
        balances.to_csv(os.path.join(outputDir, "account_balances.csv"), index=False)
        byAsset.to_csv(os.path.join(outputDir, "asset_values.csv"))
        byAddress.to_csv(os.path.join(outputDir, "address_values.csv"))
        print(f"tables written to {outputDir}/")
    return balances
