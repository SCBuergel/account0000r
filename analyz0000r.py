from tabulate import tabulate
import numpy as np
from collections import defaultdict
import pandas as pd



def printBinaryTable(data):
    """Prints a binary table out of a list with two columns where included accounts are marked with an "X" mark

    First row of the printed table contains the name of the mnemonic, first column contains the HD wallet index, the table contains "X" marks for accounts that are included in the data list

    Parameters
    ----------
    list[string, int] : a list with two columns, first one is the name of the mnemonic, second one is the index of the HD wallet index, all accounts included in the list are marked in the printed table
    """

    npData = np.array(data)
    mnemonics = sorted(set(npData[:, 0]))
    indices = sorted(set([int(elem) for elem in npData[:,1]]))
    numRows = int(max(indices)) - int(min(indices)) + 2
    tab = [[" " for j in range(len(mnemonics) + 1)] for i in range(numRows)]

    # row 0 is the header with mnemonic names
    tab[0] = ["index"] + [rep.replace(" ", "\n") for rep in mnemonics]

    # column 0 has account indices
    for i in range(1, numRows):
        tab[i][0] = i + int(min(indices)) - 1

    # "X" marks the accounts
    for i in npData:
        ind = mnemonics.index(i[0])
        tab[int(i[1]) - int(min(indices)) + 1][ind + 1] = "X"

    print(tabulate(tab, headers="firstrow", tablefmt="fancy_grid"))



def listAccountsNonZero(accounts, load0000r="ETH balance", dust=0, printCsv=False):
    """Prints list of all accounts and chain names with non-dust balance

    Parameters
    ----------
    accounts : list[account]
        List of accounts which are printed (if non-dust balance)
    load0000r : string, optional
        The load0000r module for which the ["nativeBalance"] property is printed if it is non-dust, default: "ETH balance"
    dust: number, optional
        Accounts with native balance smaller or equal to this dust value are not listed, default: 0
    printCsv: bool, optional
        True prints the list in CSV format, False prints a human-readable list, default: False
    """

    print(f"List of accounts with > {dust} {load0000r} per chain")
    for a in accounts:
        for c in a["chains"].items():
            if c[1][load0000r]["nativeBalance"] > dust:
                if printCsv:
                    print(f"{a['address']}, {c[0]}, {c[1][load0000r]['nativeBalance']},")
                else:
                    print(f'{a["address"]} ({a["mnemonic"]}, account index {a["index"]}): {c[1][load0000r]["nativeBalance"]} on {c[0]}')



def tableAccountsNonZeroBalance(accounts, load0000r="ETH balance", dust=0):
    """Prints an overview table showing all accounts with non-dust balance

    Prints and overview table where all accounts with non-dust balance are highlighted with an "X" mark and all other accounts remain unmarked. This gives a quick overview of which accounts where used at all.

    Parameters
    ----------
    accounts : list[account]
        a list of accounts loaded by account0000r
    load0000r : string, optional
        The load0000r module for which the ["nativeBalance"] property is evaluated, default: "ETH balance"
    dust : number, optional
        accounts with native balances smaller or equal to dust are ignored and not marked on overview table, default: 0
    """

    print(f"Table of accounts with > {dust} {load0000r} per chain")
    nonZeroBalanceAccounts = list(
            [ad["mnemonic"], ad["index"]] 
            for ad in accounts
            if sum(
                list(v[load0000r]["nativeBalance"]
                for v in list(ad["chains"].values()))
                ) > dust)
    printBinaryTable(nonZeroBalanceAccounts)



def listAccountsAirdropOP(accounts):
    """Prints an overview table showing all accounts which received an Optimism airdrop

    Parameters
    ----------
    accounts : list[account]
        a list of accounts loaded by account0000r
    """

    print("List of accounts which received the Optimism airdrop")
    for a in accounts:
        c = a["chains"]["Optimism"]
        airdropAmount = c["airdropOpApi"]["airdropOp"]
        if airdropAmount > 0:
            print(f'OP airdrop for {a["address"]} ({a["mnemonic"]}, account index {a["index"]}): {airdropAmount}')



def listAccountsAirdropHop(accounts):
    """Prints an overview table showing all accounts which received an HOP airdrop

    Parameters
    ----------
    accounts : list[account]
        a list of accounts loaded by account0000r
    """

    print("List of accounts which received the HOP airdrop")
    for a in accounts:
        c = a["chains"]["Ethereum Main Net"]
        airdropAmount = c["airdropHopJson"]["amountToken"]
        if airdropAmount > 0:
            print(f'HOP airdrop for {a["address"]} ({a["mnemonic"]}, account index {a["index"]}): {airdropAmount}')



def listAllNonDustBalances(accounts, chains, dust=0, atBlock=False):
    ac = pd.DataFrame(accounts)
    c = pd.DataFrame(chains)
    coinLoad0000r = "ETH balance at block" if atBlock else "ETH balance"
    tokenLoad0000r = "ERC20 balances"
    coinBalances = pd.DataFrame([
    [ac.iloc[a]['address'], chainItems[0], chainItems[1][coinLoad0000r]["nativeBalance"], c[c.name == chainItems[0]].nativeAsset.to_string(index=False).strip()]
    for a in range(ac.shape[0])
    for chainItems in ac.iloc[a]["chains"].items()
    if chainItems[1][coinLoad0000r]["nativeBalance"] > dust
    ])

    tokenBalances = pd.DataFrame()
    for a in range(ac.shape[0]):
        for chainItems in ac.iloc[a]["chains"].items():
            if tokenLoad0000r in chainItems[1]:
                for token in chainItems[1][tokenLoad0000r].values():
                    if token["erc20Balance"]['balance'] > dust:
                        tokenBalances = pd.concat([tokenBalances, pd.DataFrame([[ac.iloc[a]['address'], chainItems[0], token["erc20Balance"]['balance'], token['erc20Balance']['symbol']]])])
    
    tokenBalances = pd.concat([tokenBalances, coinBalances])
    tokenBalances.columns = ["Address", "Chain", "Balance", "Asset"]
    # print(tokenBalances)
    return tokenBalances



def tabulateNonZeroNonce(accounts):
    table = []
    for a in accounts:
        for c in a["chains"].values():
            if c["nonce"]["nonce"] > 0:
                table.append([a["mnemonic"], a["index"]])
                break
    print(table)
    printBinaryTable(table)



def tabulateAllAccounts(accounts):
    for a in accounts:
        print(a["address"])



def portfolioValue(accounts, chains, atBlock=True, assetPricesCsv="data/assetPrices.csv", storeCsv=True):
    """Prints portfolio value overview with all accounts, per asset, per account and total portfolio sum and a list of assets who are not priced in the the asset prices CSV file

    Parameters
    ----------
    accounts : list[account]
        a list of accounts loaded by account0000r
    chains : list[chain]
      	a list of chains loaded by account0000r
    atBlock : bool, optional
        reads account information with the "at block" load0000rs (for native coins and erc20 tokens), default True
    assetPriceCsv : string, optional
	    CSV file name containing asset name and price (in USD)
    storeCsv : bool, optional
        stores output CSVs for the 3 data sets that are being printed to the screen if True (default)
    """

    prices = pd.read_csv(assetPricesCsv, skipinitialspace=True)
    accountBalances = listAllNonDustBalances(accounts, chains, atBlock=atBlock)
    chainDf = pd.DataFrame(chains)
    accountBalances = accountBalances.join(prices.set_index("Asset"), on="Asset")
    accountValues = pd.DataFrame(accountBalances.Balance * accountBalances.Price)
    accountBalances = pd.concat([accountBalances, accountValues], axis=1)
    accountBalances.rename(columns = {list(accountBalances)[-1]: 'Value'}, inplace = True)
    
    prettyBalances = accountBalances.sort_values(by="Value", ascending=False)
    prettyBalances.Balance = prettyBalances.Balance.map('{:,}'.format)
    prettyBalances.Value = prettyBalances.Value.map('${:,.2f}'.format)
   
    print("All accounts and balances:")
    print(prettyBalances.to_string(index=False))
    
    valueByAsset = pd.DataFrame(accountBalances.groupby("Asset").agg({"Balance": "sum", "Value": "sum", "Price": "first"}))
    valueByAsset["Fiat value"] = valueByAsset.Value.map('${:,.2f}'.format)
    valueByAsset["Total balance"] = valueByAsset.Balance.map('{:,.2f}'.format)

    print("Assets by value:")
    print(valueByAsset.sort_values(by="Value", ascending=False)[["Total balance", "Price", "Fiat value"]].to_string())

    valueByAccount = pd.DataFrame(accountBalances.groupby("Address").sum())
    valueByAccount.drop(["Price"], axis=1, inplace=True)
    valueByAccount["Fiat value"] = valueByAccount.Value.map('${:,.2f}'.format)

    print("Accounts by total balance value:")
    print(valueByAccount.sort_values(by="Value", ascending=False)[["Fiat value"]].to_string())

    print(f"Total portfolio value: {accountBalances.Balance.mul(accountBalances.Price).sum()}")
    
    print(f"Missing asset prices for: {np.sort(accountBalances[accountBalances.Price.isna()].Asset.unique())}")
    
    if storeCsv:
        print("storing CSV files...")
        accountBalances.sort_values(by="Value", ascending=False).to_csv("data/account_balances.csv", index=False)
        accountBalances.groupby("Asset").agg({"Balance": "sum", "Value": "sum", "Price": "first"}).sort_values(by="Value", ascending=False)[["Balance", "Price", "Value"]].to_csv("data/asset_values.csv")
        accountBalances.groupby("Address").sum().sort_values(by="Value", ascending=False)[["Value"]].to_csv("data/address_values.csv")

    return accountBalances

