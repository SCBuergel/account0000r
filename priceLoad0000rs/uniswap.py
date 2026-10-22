"""Prices from Uniswap V2 style pairs, read on-chain, for tokens without a Chainlink feed.

A pair holds reserves of two tokens; their ratio is the price of one in the other. The
quote token must already be priced by an earlier loader (stablecoins or chainlink), so
list this loader after those. Reserves are read at the block of the wanted timestamp.

POOLS maps a symbol to (chain name, pair address, quote symbol). Pick the pair with the
most liquidity; a thin pool is easy to move and gives a poor price.
"""

from account0000r import blockAtTimestamp
from load0000rs.singleErc20 import ERC20_ABI
from priceLoad0000rs.base import basePriceLoad0000r
from rpc import build_web3, checksum
from utils import retry

PAIR_ABI = [
    {"inputs": [], "name": "token0", "outputs": [{"type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "token1", "outputs": [{"type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "getReserves", "stateMutability": "view", "type": "function",
     "outputs": [{"type": "uint112"}, {"type": "uint112"}, {"type": "uint32"}]},
]

POOLS = {
    "HOPR": ("Ethereum Main Net", "0x92c2fC5F306405eaB0fF0958f6D85d7F8892CF4D", "DAI"),
}


class load0000r(basePriceLoad0000r):
    def __init__(self, chains, pools=POOLS):
        self._chains = {c["name"]: c for c in chains}
        self._pools = {k.upper(): (chain, address, quote.upper()) for k, (chain, address, quote) in pools.items()}

    def name(self):
        return "uniswap"

    def version(self):
        return "0.0.1"

    def fetchPrice(self, symbol, timestamp):
        return None  # needs the quote token's price, so load() is overridden instead

    def priceInQuote(self, symbol, timestamp):
        """How many quote tokens one `symbol` token buys, from the pair's reserves."""
        chainName, address, quote = self._pools[symbol]
        chain = self._chains.get(chainName)
        if chain is None:
            print(f"[uniswap] {symbol}: pool is on {chainName}, which is not in chains.json")
            return None
        block = blockAtTimestamp(chain, timestamp)
        web3 = build_web3(chain)
        pair = web3.eth.contract(address=checksum(address), abi=PAIR_ABI)
        tokens = [retry(pair.functions.token0().call), retry(pair.functions.token1().call)]
        reserves = retry(pair.functions.getReserves().call, block_identifier=block)[:2]
        symbols, decimals = [], []
        for token in tokens:
            erc20 = web3.eth.contract(address=token, abi=ERC20_ABI)
            symbols.append(erc20.functions.symbol().call().upper())  # no retry: bytes32 symbols never decode
            decimals.append(retry(erc20.functions.decimals().call))
        if sorted(symbols) != sorted([symbol, quote]):
            print(f"[uniswap] {symbol}: pair {address} holds {symbols}, expected {[symbol, quote]}")
            return None
        base, other = (0, 1) if symbols[0] == symbol else (1, 0)
        if reserves[base] == 0:
            return None
        return (reserves[other] / 10 ** decimals[other]) / (reserves[base] / 10 ** decimals[base])

    def load(self, symbols, timestamp, resolved=None):
        resolved = resolved or {}
        prices, missing = {}, []
        for symbol in symbols:
            pool = self._pools.get(symbol.upper())
            quotePrice = resolved.get(pool[2]) if pool else None
            if pool and quotePrice is None:
                print(f"[uniswap] {symbol}: quoted in {pool[2]}, which has no price yet")
            try:
                inQuote = self.priceInQuote(symbol.upper(), timestamp) if pool and quotePrice is not None else None
            except Exception as e:
                print(f"[uniswap] error fetching {symbol}: {e}")
                inQuote = None
            if inQuote is None:
                missing.append(symbol)
            else:
                prices[symbol] = inQuote * quotePrice
        return prices, missing
