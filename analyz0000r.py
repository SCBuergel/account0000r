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


