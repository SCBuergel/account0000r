import json
from web3 import Web3
from load0000rs.base import baseLoad0000r
from utils import _exponential_backoff

class load0000r(baseLoad0000r):
    def __init__(self, skipAnalysisIfEntryExists, chain, token, metaLoad0000r, atBlock=False):
        """
        Parameters
        ----------
        skipAnalysisIfEntryExists : boolean
            true if the load0000r should quit if an entry already exists

        chain : dictionary
            the chain on which to run this load0000r

        token : dictionary
            the token for which to load the balance, has fields of:
                ["symbol"] : string
                    symbol of the token, e.g. "DAI"
                ["address"] : string
                    address of the token on which chain to run it
                ["decimals"] : 
                    decimals of the token
        atBlock : bool (optional, default: True)
            if True, it will return the load0000rs which read data at a specific block, otherwise the latest block data will be loaded

        metaLoad0000r : load0000r
            the metaLoad0000r that contains this child load0000r
        """

        self._shouldSkipAnalysisIfEntryExists = skipAnalysisIfEntryExists
        self.__chain = chain
        self.__token = token
        if atBlock:
            self.__name = "Single ERC20 balance " + self.__token["symbol"] + " on " + self.__chain["name"] + " atBlock"
        else:
            self.__name = "Single ERC20 balance " + self.__token["symbol"] + " on " + self.__chain["name"]
        self.__atBlock = atBlock
        self._metaLoad0000r = metaLoad0000r

    def name(self):
        return self.__name

    def version(self):
        return "0.0.1"

    def analyze(self, account, chain):
        if (chain["name"] != self.__chain["name"]):
            return
        if self.__atBlock:
            targetBlockNumber = chain["metadata"]["blockNumberByTimestamp"]["blockNumber"]
        else:
            targetBlockNumber = "latest"

        web3 = Web3(Web3.HTTPProvider(chain["api"]))
        erc20BalanceABI = """[
        {"inputs":[{"internalType":"address","name":"tokenHolder","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}
        ]
        """
            
        # check if token has been deployed by target block already, otherwise the erc20 calls would fail
        code = _exponential_backoff(web3.eth.get_code, self.__token["address"], block_identifier=targetBlockNumber)
        if (len(code) > 2):
            erc20 = web3.eth.contract(address=self.__token["address"], abi=erc20BalanceABI)
            balance = _exponential_backoff(erc20.functions.balanceOf(account).call, block_identifier=targetBlockNumber) / 10**self.__token["decimals"]
        else:
            print(f"token {self.__token['symbol']} not deployed at block {targetBlockNumber} on chain {chain['name']}")
            balance = 0
        # print(f"balance of {account} is {balance} {self.__token['symbol']} at block {targetBlockNumber}")
        newEntry = self.createEmptyAccountEntry()
        newEntry["erc20Balance"] = {
                    "symbol": self.__token["symbol"],
                    "balance": balance
                }
        return newEntry

    def loadTokenMetadata(self):
        """Loads token symbol and decimals and stores in class property

        Returns
        -------
        dictionary
            the self.__token object that should contain the decimals and symbol checked after the call
        """
        print(f"{self.__token['symbol']} on {self.__chain['name']}")
        web3 = Web3(Web3.HTTPProvider(self.__chain["api"]))
        erc20MetadataABI = """[
        {"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"pure","type":"function"},
        {"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
        {"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"}
        ]
        """
            
        erc20 = web3.eth.contract(address=self.__token["address"], abi=erc20MetadataABI)

        # load decimal and symbol only if it does not yet exist in the metadata
        if ("decimals" not in self.__token):
            self.__token["decimals"] = int(_exponential_backoff(erc20.functions.decimals().call))
        
        # since MKR and SAI are not ERC20 compatible we have to exclude them from this check 
        if ("symbol" not in self.__token and self.__token["symbol"] != "MKR" and self.__token["symbol"] != "SAI"):
            symbol = _exponential_backoff(erc20.functions.symbol().call)
            name = _exponential_backoff(erc20.functions.name().call)
            if (symbol != self.__token["symbol"]):
                print(f"Token symbol of load0000r {self.name()} does not match, expected {self.__token['symbol']} but got {symbol} from chain")

        return self.__token
