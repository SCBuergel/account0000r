from web3 import Web3
from load0000rs.base import baseLoad0000r

class load0000r(baseLoad0000r):
    def name(self):
        return "nonce"

    def version(self):
        return "0.0.1"

    def analyze(self, account, chain):
        web3 = Web3(Web3.HTTPProvider(chain["api"]))
        nonce = web3.eth.getTransactionCount(account)
        newEntry = self.createEmptyAccountEntry()
        newEntry["nonce"] = nonce
        return newEntry
