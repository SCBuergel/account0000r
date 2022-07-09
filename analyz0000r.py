from tabulate import tabulate
import numpy as np
from collections import defaultdict
  
def printBinaryTable(data):
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


# prints list of all accounts and chain names with non-zero balance
def listAccountsNonZero(accounts):
    print("List of accounts with non-dust balance per chain")
    for a in accounts:
        for c in a["chains"].items():
            if c[1]["ETH balance"]["nativeBalance"] > 0:
                print(f'{a["address"]} ({a["mnemonic"]}, account index {a["index"]}): {c[1]["ETH balance"]["nativeBalance"]} on {c[0]}')

# prints all accounts with non-zero balance (ignoring dust)
def tableAccountsNonZeroBalance(accounts):
    print("Table of accounts with non-dust balance on any chain")
    nonZeroBalanceAccounts = list([ad["mnemonic"], ad["index"]] for ad in accounts if sum(list(v["ETH balance"]["nativeBalance"] for v in list(ad["chains"].values()))) > 0.001)
    printBinaryTable(nonZeroBalanceAccounts)

# all accounts with OP airdrop
def listAccountsAirdropOP(accounts):
    print("List of accounts who received an Optimism airdrop")
    for a in accounts:
        c = a["chains"]["Optimism"]
        if c["airdropOpApi"]["airdropOp"] > 0:
            print(f'OP airdrop for {a["address"]} ({a["mnemonic"]}, account index {a["index"]}): {c["airdropOpApi"]["airdropOp"]}')


