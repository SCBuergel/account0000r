"""Balance of one ERC-20 token on one chain. Built by account0000r.generateTokenLoad0000rs."""

import threading

from load0000rs.base import baseLoad0000r, targetBlock
from rpc import build_web3, checksum
from utils import retry

ERC20_ABI = [
    {"inputs": [{"name": "tokenHolder", "type": "address"}], "name": "balanceOf",
     "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}],
     "stateMutability": "view", "type": "function"},
]


class load0000r(baseLoad0000r):
    def __init__(self, skipAnalysisIfEntryExists, chain, token, metaLoad0000r, atBlock=False):
        """token is a dict from chains.json with "symbol", "address" and, once
        loadTokenMetadata() ran, "decimals"."""
        self._shouldSkipAnalysisIfEntryExists = skipAnalysisIfEntryExists
        self._chain = chain
        self._token = token
        self._atBlock = atBlock
        self._metaLoad0000r = metaLoad0000r
        self._deployedAt = {}  # block -> whether the token contract has code there
        self._deployedLock = threading.Lock()

    def name(self):
        suffix = " atBlock" if self._atBlock else ""
        return f"Single ERC20 balance {self._token['symbol']} on {self._chain['name']}{suffix}"

    def version(self):
        return "0.0.1"

    def _contract(self, web3):
        return web3.eth.contract(address=checksum(self._token["address"]), abi=ERC20_ABI)

    def appliesTo(self, chain):
        return chain["name"] == self._chain["name"]

    def analyze(self, account, chain):
        if not self.appliesTo(chain):
            return None
        block = targetBlock(chain, self._atBlock)
        web3 = build_web3(chain)
        if self._isDeployed(web3, block):
            raw = retry(self._contract(web3).functions.balanceOf(account).call, block_identifier=block)
            balance = raw / 10 ** self._token["decimals"]
        else:
            print(f"token {self._token['symbol']} not deployed at block {block} on {chain['name']}")
            balance = 0
        entry = self.createEmptyAccountEntry()
        entry["erc20Balance"] = {"symbol": self._token["symbol"], "balance": balance}
        return entry

    def _isDeployed(self, web3, block):
        """Whether the token contract has code at `block`; balanceOf on a contract that
        did not exist yet would revert. Depends on the token and block only, not on the
        account, so it is fetched once per loader and reused for every account. The lock
        makes concurrent tasks of the same token wait for that one fetch instead of each
        asking the chain themselves."""
        with self._deployedLock:
            if block not in self._deployedAt:
                code = retry(web3.eth.get_code, checksum(self._token["address"]), block_identifier=block)
                self._deployedAt[block] = len(code) > 0
            return self._deployedAt[block]

    def loadTokenMetadata(self):
        """Fill in token["decimals"] from the chain if missing and warn when the on-chain
        symbol differs from the configured one. Returns the token dict."""
        contract = self._contract(build_web3(self._chain))
        if "decimals" not in self._token:
            self._token["decimals"] = int(retry(contract.functions.decimals().call))
        try:
            onChain = contract.functions.symbol().call()
        except Exception:
            onChain = None  # e.g. MKR and SAI return bytes32, which is not decodable as string
        if onChain and onChain.upper() != self._token["symbol"].upper():
            print(f"  symbol mismatch on {self._chain['name']}: configured "
                  f"{self._token['symbol']}, chain says {onChain}")
        return self._token
