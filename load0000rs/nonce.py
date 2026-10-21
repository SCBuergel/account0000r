"""Transaction count of an account at the latest block. Non-zero means the account was used."""

from load0000rs.base import baseLoad0000r
from rpc import build_web3
from utils import retry

NAME = "nonce"


class load0000r(baseLoad0000r):
    _shouldSkipAnalysisIfEntryExists = True

    def name(self):
        return NAME

    def version(self):
        return "0.0.1"

    def analyze(self, account, chain):
        web3 = build_web3(chain)
        entry = self.createEmptyAccountEntry()
        entry["nonce"] = retry(web3.eth.get_transaction_count, account)
        return entry
