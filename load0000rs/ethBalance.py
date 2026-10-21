"""Native coin balance (ETH, xDAI, MATIC, ...) of an account."""

from load0000rs.base import baseLoad0000r, targetBlock
from rpc import build_web3
from utils import retry

NAME = "ETH balance"
NAME_AT_BLOCK = "ETH balance at block"


class load0000r(baseLoad0000r):
    def __init__(self, atBlock=False, skipAnalysisIfEntryExists=False):
        self._atBlock = atBlock
        self._shouldSkipAnalysisIfEntryExists = skipAnalysisIfEntryExists

    def name(self):
        return NAME_AT_BLOCK if self._atBlock else NAME

    def version(self):
        return "0.0.1"

    def analyze(self, account, chain):
        web3 = build_web3(chain)
        wei = retry(web3.eth.get_balance, account, targetBlock(chain, self._atBlock))
        entry = self.createEmptyAccountEntry()
        entry["nativeBalance"] = wei / 1e18
        return entry
