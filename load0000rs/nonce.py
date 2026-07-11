from load0000rs.base import baseLoad0000r
from utils import _exponential_backoff
from rpc import build_web3

class load0000r(baseLoad0000r):
    def __init__(self):
        self._shouldSkipAnalysisIfEntryExists = True

    def name(self):
        return "nonce"

    def version(self):
        return "0.0.1"

    def analyze(self, account, chain):
        web3 = build_web3(chain)
        nonce = _exponential_backoff(web3.eth.get_transaction_count, account)
        newEntry = self.createEmptyAccountEntry()
        newEntry["nonce"] = nonce
        return newEntry
