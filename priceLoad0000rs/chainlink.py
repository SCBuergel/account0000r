"""USD prices from Chainlink price feeds, read on-chain through the configured RPCs.

A feed is a contract whose latestRoundData() returns the price its oracles last agreed
on. Calling it at the block of the wanted timestamp (an archive endpoint is needed for
past dates) gives the price back then: no API, no key, and nothing leaves the machine
but RPC calls that the balance loaders make anyway.

FEEDS maps a symbol to the chain the feed lives on and its proxy address. Feeds for
Ethereum assets live on Ethereum; ARB, GNO and OP are on their own chains. EURE (Monerium
EUR) is priced by the EUR/USD feed. Find more at https://data.chain.link/feeds.
"""

from account0000r import blockAtTimestamp
from priceLoad0000rs.base import basePriceLoad0000r
from rpc import build_web3, checksum
from utils import retry, ts_to_utc

FEED_ABI = [
    {"inputs": [], "name": "decimals", "outputs": [{"type": "uint8"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "latestRoundData", "stateMutability": "view", "type": "function",
     "outputs": [{"name": "roundId", "type": "uint80"}, {"name": "answer", "type": "int256"},
                 {"name": "startedAt", "type": "uint256"}, {"name": "updatedAt", "type": "uint256"},
                 {"name": "answeredInRound", "type": "uint80"}]},
]

FEEDS = {
    "ETH": ("Ethereum Main Net", "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419"),
    "ENS": ("Ethereum Main Net", "0x5C00128d4d1c2F4f652C267d7bcdD7aC99C16E16"),
    "EURE": ("Ethereum Main Net", "0xb49f677943BC038e9857d61E7d053CaA2C1734C1"),  # EUR / USD
    "MATIC": ("Ethereum Main Net", "0x7bAC85A8a13A4BcD8abb3eB7d6b4d632c5a57676"),
    "BNB": ("Ethereum Main Net", "0x14e613AC84a31f709eadbdF89C6CC390fDc9540A"),
    "AAVE": ("Ethereum Main Net", "0x547a514d5e3769680Ce22B2361c10Ea13619e8a9"),
    "UNI": ("Ethereum Main Net", "0x553303d460EE0afB37EdFf9bE42922D8FF63220e"),
    "CRV": ("Ethereum Main Net", "0xCd627aA160A6fA45Eb793D19Ef54f5062F20f33f"),
    "MKR": ("Ethereum Main Net", "0xec1D1B3b0443256cc3860e24a46F108e699484Aa"),
    "ARB": ("Arbitrum", "0xb2A824043730FE05F3DA2efaFa1CBbe83fa548D6"),
    "GNO": ("Gnosis Chain", "0x22441d81416430A54336aB28765abd31a792Ad37"),
    "OP": ("Optimism", "0x0D276FC14719f9292D5C1eA2198673d1f4269246"),
}

MAX_AGE = 3 * 24 * 3600  # a feed answer older than this at the wanted time is not trusted


class load0000r(basePriceLoad0000r):
    def __init__(self, chains, feeds=FEEDS):
        """chains: the dicts from chains.json; a feed whose chain is not among them is
        skipped with a message."""
        self._chains = {c["name"]: c for c in chains}
        self._feeds = {k.upper(): v for k, v in feeds.items()}

    def name(self):
        return "chainlink"

    def version(self):
        return "0.0.1"

    def fetchPrice(self, symbol, timestamp):
        feed = self._feeds.get(symbol.upper())
        if feed is None:
            return None
        chainName, address = feed
        chain = self._chains.get(chainName)
        if chain is None:
            print(f"[chainlink] {symbol}: feed is on {chainName}, which is not in chains.json")
            return None
        block = blockAtTimestamp(chain, timestamp)
        contract = build_web3(chain).eth.contract(address=checksum(address), abi=FEED_ABI)
        decimals = retry(contract.functions.decimals().call, block_identifier=block)
        _, answer, _, updatedAt, _ = retry(contract.functions.latestRoundData().call, block_identifier=block)
        if answer <= 0 or timestamp - updatedAt > MAX_AGE:  # a dead feed repeats its last answer forever
            print(f"[chainlink] {symbol}: feed answer {answer} from {ts_to_utc(updatedAt)} not usable")
            return None
        return answer / 10 ** decimals
