from tabulate import tabulate
import numpy as np
from collections import defaultdict



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
    nonZeroBalanceAccounts = list([ad["mnemonic"], ad["index"]] for ad in accounts if sum(list(vi[load0000r]["nativeBalance"] for v in list(ad["chains"].values()))) > dust)
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

