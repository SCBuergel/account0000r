import json
from web3 import Web3
from load0000rs.base import baseLoad0000r

class load0000r(baseLoad0000r):
    def __init__(self):
        self._shouldSkipAnalysisIfEntryExists = True

    def name(self):
        return "ETH balance at block"

    def version(self):
        return "0.0.1"

    def analyze(self, account, chain):
        targetBlockNumber = chain["metadata"]["blockNumberByTimestamp"]["blockNumber"]

        web3 = Web3(Web3.HTTPProvider(chain["api"]))
        balance = web3.eth.get_balance(account, targetBlockNumber)/1e18
        newEntry = self.createEmptyAccountEntry()
        newEntry["nativeBalance"] = balance
        return newEntry

