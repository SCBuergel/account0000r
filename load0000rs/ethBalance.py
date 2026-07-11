import json
from load0000rs.base import baseLoad0000r
from utils import _exponential_backoff
from rpc import build_web3

class load0000r(baseLoad0000r):
    def __init__(self, atBlock=False, skipAnalysisIfEntryExists=False):
        self.__atBlock = atBlock
        self._shouldSkipAnalysisIfEntryExists = skipAnalysisIfEntryExists

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
            
        web3 = build_web3(chain)
        balance = _exponential_backoff(web3.eth.get_balance, account, targetBlockNumber)/1e18
        newEntry = self.createEmptyAccountEntry()
        newEntry["nativeBalance"] = balance
        return newEntry

