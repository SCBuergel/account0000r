import json
from web3 import Web3
from load0000rs.base import baseLoad0000r

class load0000r(baseLoad0000r):
    def name(self):
        return "ERC-20 balance at block"

    def version(self):
        return "0.0.1"

    def analyze(self, account, chain):
        chains = json.load(open("chains.json"))
        chainIndex = chains.index(chain)
        blockNumbersEnd2021 = json.load(open("data/blockNumbersEnd2021.json"))
        targetBlockNumber = blockNumbersEnd2021[chainIndex]

        web3 = Web3(Web3.HTTPProvider(chain["api"]))
        tokenIndex = 18
        erc20BalanceABI = """[
        {"inputs":[{"internalType":"address","name":"tokenHolder","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
        {"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"pure","type":"function"},
        {"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
        {"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"}
        ]
        """
        tokenAddress = chain["tokens"][tokenIndex]["address"]
        erc20 = web3.eth.contract(address=tokenAddress, abi=erc20BalanceABI)
        name = erc20.functions.name().call()
        decimals = erc20.functions.decimals().call()
        balance = erc20.functions.balanceOf(account["address"]).call(block_identifier=targetBlockNumber)
        print(f"balance of {account['address']} is {balance/10**decimals} {name}s at block {targetBlockNumber}")
        newEntry = self.createEmptyAccountEntry()
        newEntry["nativeBalance"] = balance
        return newEntry



