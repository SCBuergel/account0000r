import json
from web3 import Web3
from load0000rs.base import baseLoad0000r

class load0000r(baseLoad0000r):
    def __init__(self):
        self._isMetaLoad0000r = True

    def name(self):
        return "ERC20 balances" 
    
    def version(self):
        return "0.0.1"

    def analyze(self, account, chain):
        return
        # TODO: throw exception to make sure a metadaLoad0000r cannot actually analyze anything by accident
