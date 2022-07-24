from datetime import datetime
import json
from hdwallet import BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet
from hdwallet.derivations import BIP44Derivation
from hdwallet.utils import generate_mnemonic
#pip install hdwallet

def loadAccountMetadata(load0000rs, accounts, chainsFileName="chains.json"):
    chains = json.load(open("chains.json"))
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



# only load mnemonics if you know what you are doing
# and on a computer that you fully trust
# otherwise all funds association with these mnemonics will be at risk

# optionally an existing accounts list can be passed
# existing elements in the list are not overwritten
def accountsFromSecrets(secrets, accounts=None):

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

        # Get Ethereum BIP44HDWallet information's from address index
        for address_index in range(accountOffset, numAccounts + accountOffset):
            bip44_hdwallet.clean_derivation()
            # Derivation from Ethereum BIP44 derivation path
            bip44_derivation: BIP44Derivation = BIP44Derivation(
                cryptocurrency=EthereumMainnet, account=0, change=False, address=address_index
            )
            # Drive Ethereum BIP44HDWallet
            bip44_hdwallet.from_path(path=bip44_derivation)
            # Print address_index, path, address and private_key
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
    file = open(accountFileName, "w")
    prettyAccounts = json.dumps(accounts, indent=2)
    file.write(prettyAccounts)
    file.close()
    return accountFileName
