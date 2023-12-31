import json
from web3 import Web3
from load0000rs.base import baseLoad0000r
from utils import _exponential_backoff

class load0000r(baseLoad0000r):
    def __init__(self, atBlock=False):
        self.__atBlock = atBlock

    def name(self):
        if self.__atBlock:
            return "ETH balance at block"
        else:
            return "ETH balance"

    def version(self):
        return "0.0.1"

    def analyze(self, account, chain):
        if self.__atBlock:
            targetBlockNumber = chain["metadata"]["blockNumberByTimestamp"]["blockNumber"]
        else:
            targetBlockNumber = "latest"
            
        web3 = Web3(Web3.HTTPProvider(chain["api"]))
        balance = _exponential_backoff(web3.eth.get_balance, account, targetBlockNumber)/1e18
        newEntry = self.createEmptyAccountEntry()
        newEntry["nativeBalance"] = balance
        return newEntry

