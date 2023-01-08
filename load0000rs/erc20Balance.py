import json
from web3 import Web3
from load0000rs.base import baseLoad0000r

class load0000r(baseLoad0000r):
    def __init__(self, skipAnalysisIfEntryExists):
        self._shouldSkipAnalysisIfEntryExists = skipAnalysisIfEntryExists

    def name(self):
        return "ERC-20 balance"

    def version(self):
        return "0.0.1"

    def analyze(self, account, chain):
        targetBlockNumber = "latest"
        web3 = Web3(Web3.HTTPProvider(chain["api"]))
        erc20BalanceABI = """[
        {"inputs":[{"internalType":"address","name":"tokenHolder","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
        {"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"pure","type":"function"},
        {"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
        {"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"}
        ]
        """
        tokenBalances = []
        for token in chain["tokens"]:
            tokenAddress = token["address"]
            
            # check if token has been deployed by target block already, otherwise the erc20 calls would fail
            code = web3.eth.get_code(tokenAddress, block_identifier=targetBlockNumber)
            if (len(code) > 2):
                erc20 = web3.eth.contract(address=tokenAddress, abi=erc20BalanceABI)
                # name = erc20.functions.name().call()
                decimals = int(erc20.functions.decimals().call())
                balance = erc20.functions.balanceOf(account).call(block_identifier=targetBlockNumber) / 10**decimals
            else:
                balance = 0
            tokenBalances.append({
                    "name": token["name"],
                    "balance": balance
                })
            print(f"balance of {account} is {balance} {token['name']}")
        newEntry = self.createEmptyAccountEntry()
        newEntry["erc20Balances"] = tokenBalances
        return newEntry

