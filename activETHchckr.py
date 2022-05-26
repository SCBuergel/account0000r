from web3 import Web3
import json
import sys

from hdwallet import BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet
from hdwallet.derivations import BIP44Derivation
from hdwallet.utils import generate_mnemonic
from typing import Optional
#pip install hdwallet

# TODO:
"""
create separate functions for
# createAccountsFromMnemonics
# storeAccounts
# loadAccounts
# analyzeAccounts

which use a storage format of accounts that's consistent:
[{
  "account": "0x0000000000000000000000000000000000001337",
  "use": "manual edits here",
  "mnemonic": "description of mnemonic",
  "path": "m/44'/60'/0'/0/123"
  "activeOnChains": [
    {
      "name": "EthereumMainNet",
      "balance": 0.1,
      "nonce": 12
    },
    {
      "name": "Polygon",
      "balance": 12.3,
      "nonce": 42
    }]
}]
"""


def accountsFromSecrets(secrets, hdPath="m/44'/60'/0'/0", numAccounts=10):

    accounts = [] # we will populate this and then return it

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

        print("Mnemonic:", bip44_hdwallet.mnemonic())

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
            print(f"({address_index}) {bip44_hdwallet.path()} {bip44_hdwallet.address()} 0x{bip44_hdwallet.private_key()}")
            accounts.append({
                "address": bip44_hdwallet.address(),
                "index": address_index,
                "use": "",
                "mnemonic": "",
                "chains": {}
            })
        return accounts


secrets = json.load(open("secrets.json"))
print(json.dumps(secrets, indent=2))
accounts = accountsFromSecrets(secrets)
print(accounts)

accounts = json.load(open("accounts.json"))
# print(json.dumps(accounts, indent=2))
chains = json.load(open("chains.json"))


"""
for c in chains:
    print(c["name"], ":")
    web3 = Web3(Web3.HTTPProvider(c["api"]))
    for a in accounts:
        balance = web3.eth.getBalance(a["account"])/1e18
        nonce = web3.eth.getTransactionCount(a["account"])
        if balance > 0 or nonce > 0:
            print(a["account"])
            print("Balance: ", balance)
            print("Nonce: ", nonce)
            print("----------")
    print("==========")
"""

