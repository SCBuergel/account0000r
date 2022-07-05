from web3 import Web3
from analyzeBase import analyzeBase

class analyzeNonce(analyzeBase):
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
