from datetime import datetime
import json
from hdwallet import BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet
from hdwallet.derivations import BIP44Derivation
from hdwallet.utils import generate_mnemonic
#pip install hdwallet
from web3 import Web3
from web3.middleware import geth_poa_middleware

def loadAccountMetadata(load0000rs, accounts, chains):
    """Takes a list of accounts and returns them enriched with metadata obtained from a list of load0000rs that are passed

    The load0000rs are run for every account on every chain that is passed to this function. The list of all accounts that contains the resulting analysis results is returned.

    Parameters
    ----------
    load0000rs : list[baseLoad0000r]
        List of loadors which are derived fomr baseLoad0000r and for which the analyze function is executed
    accounts : list[account]
        List of accounts which are analyzed, each account in the list is enriched with a load0000r result for each load0000r that is passed
    chains : list[chains]
        List of chains for which each load0000r is run

    Returns
    -------
    list
        a list of accounts with the analysis results included for each account
    """

    print("checking ", len(accounts), " accounts on ", len(chains), " chains:")
    for ci in range(len(chains)):
        c = chains[ci]
        for a in range(len(accounts)):
            print(f"progress: {(ci * len(accounts) + a) / (len(chains) * len(accounts)) * 100:.2f}%")
            address = accounts[a]["address"]
            for load0000r in load0000rs:
                newEntry = load0000r.analyze(address, c)
                if ("chains" not in accounts[a]):
                    accounts[a]["chains"] = {}
                if (c["name"] not in accounts[a]["chains"]):
                    accounts[a]["chains"][c["name"]] = {}

                accounts[a]["chains"][c["name"]][load0000r.name()] = newEntry
    return accounts



def accountsFromSecrets(secrets, accounts=None):
    """Generats accounts from secrets which comprise mnemonic and optional passphrase

    Warning! Only load mnemonics into software on a machine that you both fully trust, you might loose all your funds if these mnemonics are leaked or logged anywhere!

    Parameters
    ----------
    secrets : list[secret]
        A list of objects comprising fields for:
            ["mnemonic"]: The mnemonic from which accounts are derived
            ["passphrase"] (optional, default: ""): The passphrase from which the accounts are derived in combination with the mnemonics
            ["hdPath"] (optional, default: "m/44'/60'/0'/0"): The HD key path from which the accounts are derived
            ["numAccounts"] (optional, default: 10): The number of accounts to be derived
            ["accountOffset"] (optional, default: 0): The offset index for which the first account is derived
            ["description"] (optional, default: ""): The description of the mnemonic, used as a description for each account also
    accounts : list[account], optional
        a list of accounts to which the newly derived are appended. If a newly generated account already exists on the list, it is ignored and not overwritten or duplicated

    Returns
    -------
    list
        a list of accounts with the analysis results included for each account
    """

    if accounts == None:
        accounts = []

    for s in secrets:
        MNEMONIC = s["mnemonic"]
        PASSPHRASE = s["passphrase"] if ("passphrase" in s) else ""
        hdPath = s["hdPath"] if ("hdPath" in s) else "m/44'/60'/0'/0"
        numAccounts = int(s["numAccounts"]) if ("numAccounts" in s) else 10
        accountOffset = int(s["accountOffset"]) if ("accountOffset" in s) else 0
        description = s["description"] if ("description" in s) else ""

        bip44_hdwallet: BIP44HDWallet = BIP44HDWallet(cryptocurrency=EthereumMainnet)
        # Get Ethereum BIP44HDWallet from mnemonic
        bip44_hdwallet.from_mnemonic(
                mnemonic=MNEMONIC, language="english", passphrase=PASSPHRASE
                )

        # split the string hdPath into its elements and skip the first "m" element
        pathElements = hdPath.split("/")[1:]
        for elem in pathElements:
            # remove a potentially trailing "'"
            numElem = elem.split("'")[0]
            bip44_hdwallet.from_index(int(numElem), hardened=(elem.endswith("'")))

        # Get Ethereum BIP44HDWallet informations from address index
        for address_index in range(accountOffset, numAccounts + accountOffset):
            bip44_hdwallet.clean_derivation()
            # Derivation from Ethereum BIP44 derivation
            bip44_derivation: BIP44Derivation = BIP44Derivation(
                    cryptocurrency=EthereumMainnet, account=0, change=False, address=address_index
                    )
            # Drive Ethereum BIP44HDWallet
            bip44_hdwallet.from_path(path=bip44_derivation)
            address = bip44_hdwallet.address()

            # only append new entry if it's not on the account list already
            if not any(i["address"]==address for i in accounts):
                accounts.append({
                    "address": address,
                    "index": address_index,
                    "use": "",
                    "mnemonic": description,
                    "chains": {}
                    })
                return accounts




# this will create or overwrite the file
def storeAccounts(accounts, accountFileName="data/accounts-" + datetime.now().strftime("%Y-%m-%d--%H-%M-%S") + ".json"):
    """Writes a list of accounts as pretty formatted JSON to a file, file will be overwritten if it already exist

    Parameters
    ----------
    accounts : list[account]
        a list of accounts loaded by account0000r
    accountFileName : string, optional
        filename to which to write, by default data is written to the data folder and the file is post-fixed with the current data and time
    """
    file = open(accountFileName, "w")
    prettyAccounts = json.dumps(accounts, indent=2)
    file.write(prettyAccounts)
    file.close()
    return accountFileName



def getBlockNumberByTime(timestamp, chains):
    """Returns list of block numbers at a timestamp on various chains

    Returns a list of block numbers that correspond to the timestamp passed as first parameter for all chains that are passed as the second argument. Doing binary search on blocks that are obtained via each chain's RPC API.

    Parameters
    ----------
    timestamp : int
        timestamp for which block numbers should be identified for each chain. The timestamp has to exist on each chain.
    chains : list[chain]
        list of chain objects that have "api" field with RPC endpoint and "name" field with the name of that chain

    Returns
    -------
    list
        a list of block numbers of each chain corresponding to timestamp, same order as the chains list
    """

    blockNos = []
    for c in range(len(chains)):
        chain = chains[c]
        web3 = Web3(Web3.HTTPProvider(chain["api"]))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        smallerBlock = web3.eth.get_block(1, False)
        biggerBlock = web3.eth.get_block("latest")
        if (timestamp < smallerBlock.timestamp):
            print(f"Error: targer timestamp {timestamp} is earlier than the timestampe of block number 1 on {chain['name']} which is {smallerBlock.timestamp}")
            return
        elif (timestamp > biggerBlock.timestamp):
            print(f"Error: target timestamp {timestamp} is later than the timestampe of the latest block (block number {biggerBlock.number}) on {chain['name']} which is {biggerBlock.timestamp}")
            return
        else:
            while (True):
                # print(f"{smallerBlock.number}:{smallerBlock.timestamp}")
                # print(f"{biggerBlock.number}:{biggerBlock.timestamp}")
                nextBlockNo = int((biggerBlock.number + smallerBlock.number) / 2)
                nextBlock = web3.eth.get_block(nextBlockNo, False)
                if (nextBlock.timestamp >= timestamp):
                    if (nextBlock.number == biggerBlock.number):
                        # print(f"we're close enough for a rounding error, quitting here")
                        break;
                    biggerBlock = nextBlock
                else:
                    if (nextBlock.number == smallerBlock.number):
                        # print(f"we're close enough for a rounding error, quitting here")
                        break;
                    smallerBlock = nextBlock

        print(f"block {nextBlock.number} happened at time {nextBlock.timestamp}")
        blockNos.append(nextBlock.number)
    return blockNos

