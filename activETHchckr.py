from web3 import Web3
import json
import sys
from datetime import datetime

from hdwallet import BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet
from hdwallet.derivations import BIP44Derivation
from hdwallet.utils import generate_mnemonic
from typing import Optional
#pip install hdwallet


# optionally an existing accounts list can be passed
# existing elements in the list are not overwritten
def accountsFromSecrets(secrets, accounts=[], hdPath="m/44'/60'/0'/0", numAccounts=10):

    for s in secrets:
        MNEMONIC = s["mnemonic"]
        PASSPHRASE = s["passphrase"]
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
        for address_index in range(numAccounts):
            bip44_hdwallet.clean_derivation()
            # Derivation from Ethereum BIP44 derivation path
            bip44_derivation: BIP44Derivation = BIP44Derivation(
                cryptocurrency=EthereumMainnet, account=0, change=False, address=address_index
            )
            # Drive Ethereum BIP44HDWallet
            bip44_hdwallet.from_path(path=bip44_derivation)
            # Print address_index, path, address and private_key
            # print(f"({address_index}) {bip44_hdwallet.path()} {bip44_hdwallet.address()} 0x{bip44_hdwallet.private_key()}")
            address = bip44_hdwallet.address()

            # only append new entry if it's not on the account list already
            if not any(i["address"]==address for i in accounts):
                accounts.append({
                    "address": address,
                    "index": address_index,
                    "use": "",
                    "mnemonic": s["description"],
                    "chains": []
                })
    return accounts



# this will create or overwrite the file
def storeAccounts(accounts, accountFileName="accounts-" + datetime.now().strftime("%Y-%m-%d--%H-%M-%S") + ".json"):
    file = open(accountFileName, "w")
    prettyAccounts = json.dumps(accounts, indent=2)
    file.write(prettyAccounts)
    file.close()



def analyzeAccounts(accounts, chainsFileName="chains.json"):
    chains = json.load(open("chains.json"))
    for c in chains:
        web3 = Web3(Web3.HTTPProvider(c["api"]))
        for a in range(len(accounts)):
            address = accounts[a]["address"]
            balance = web3.eth.getBalance(address)/1e18
            nonce = web3.eth.getTransactionCount(address)
            if balance > 0 or nonce > 0:
                accounts[a]["chains"].append({
                    "name": c["name"],
                    "balance": balance,
                    "nonce": nonce
                })



secrets = json.load(open("secrets.json"))
accounts = accountsFromSecrets(secrets)
analyzeAccounts(accounts)
storeAccounts(accounts)

