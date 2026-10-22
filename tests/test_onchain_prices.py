"""Stablecoin, Chainlink and Uniswap price loaders against fake contracts (no network)."""

import time

import pytest

import account0000r
from priceLoad0000rs import chainlink, stable, uniswap


def test_stablecoins_are_one_dollar():
    loader = stable.load0000r()
    assert loader.load(["DAI", "usdc.e", "HOPR"], 0) == ({"DAI": 1.0, "usdc.e": 1.0}, ["HOPR"])


def test_block_at_timestamp(chains, monkeypatch):
    assert account0000r.blockAtTimestamp(chains[0], int(time.time())) == "latest"
    assert account0000r.blockAtTimestamp(chains[0], 1735689600) == 12345  # stored by step 2

    class Block(dict):  # web3 blocks allow both block["timestamp"] and block.timestamp
        __getattr__ = dict.__getitem__

    class FakeEth:  # block n was mined at second 10 * n; latest is block 100
        def get_block(self, n):
            n = 100 if n == "latest" else n
            return Block(timestamp=10 * n, number=n)

    monkeypatch.setattr(account0000r, "build_web3", lambda chain: type("W", (), {"eth": FakeEth()})())
    assert account0000r.blockAtTimestamp(chains[1], 555) == 55
    assert chains[1]["metadata"]["blockNumberByTimestamp"] == {"timestamp": 555, "blockNumber": 55}
    with pytest.raises(ValueError):
        account0000r.blockAtTimestamp(chains[1], 5000)  # after the latest block


class FakeFunction:
    def __init__(self, value):
        self._value = value

    def call(self, block_identifier=None):
        return self._value


class FakeContract:
    """Answers every ABI function from `values`: name -> value."""

    def __init__(self, values):
        self.functions = type("F", (), {name: staticmethod(lambda v=value: FakeFunction(v))
                                        for name, value in values.items()})()


def fakeWeb3(contracts):
    """A build_web3 stand-in: address -> FakeContract."""
    eth = type("Eth", (), {"contract": lambda self, address, abi: contracts[address]})()
    return lambda chain: type("W", (), {"eth": eth})()


def test_chainlink_scales_by_decimals_and_rejects_stale_answers(chains, monkeypatch):
    feeds = {"ETH": ("Testnet", "0x" + "a" * 40), "OLD": ("Testnet", "0x" + "b" * 40),
             "FAR": ("Nowhere", "0x" + "c" * 40)}
    eoy = 1735689600
    contracts = {
        chainlink.checksum("0x" + "a" * 40): FakeContract({"decimals": 8, "latestRoundData": (1, 333412345678, 0, eoy - 3600, 1)}),
        chainlink.checksum("0x" + "b" * 40): FakeContract({"decimals": 8, "latestRoundData": (1, 100, 0, eoy - 10 * 86400, 1)}),
    }
    monkeypatch.setattr(chainlink, "build_web3", fakeWeb3(contracts))
    loader = chainlink.load0000r(chains, feeds)
    prices, missing = loader.load(["ETH", "OLD", "FAR", "XYZ"], eoy)
    assert prices == {"ETH": 3334.12345678}
    assert missing == ["OLD", "FAR", "XYZ"]
    # a dead feed repeats its last answer at "latest" too and must be rejected there as well
    now = int(time.time())
    contracts[chainlink.checksum("0x" + "a" * 40)] = FakeContract({"decimals": 8, "latestRoundData": (1, 10 ** 8, 0, now - 3600, 1)})
    contracts[chainlink.checksum("0x" + "b" * 40)] = FakeContract({"decimals": 8, "latestRoundData": (1, 10 ** 8, 0, now - 400 * 86400, 1)})
    assert loader.load(["ETH", "OLD"], now) == ({"ETH": 1.0}, ["OLD"])


def test_uniswap_prices_from_reserves_in_the_quote_token(chains, monkeypatch):
    pair, hopr, dai = ("0x" + c * 40 for c in "123")
    contracts = {
        uniswap.checksum(pair): FakeContract({"token0": dai, "token1": hopr,
                                              "getReserves": (20_626 * 10 ** 18, 230_514 * 10 ** 18, 0)}),
        dai: FakeContract({"symbol": "DAI", "decimals": 18}),
        hopr: FakeContract({"symbol": "HOPR", "decimals": 18}),
    }
    monkeypatch.setattr(uniswap, "build_web3", fakeWeb3(contracts))
    loader = uniswap.load0000r(chains, {"HOPR": ("Testnet", pair, "DAI")})
    assert loader.load(["HOPR", "XYZ"], 1735689600, resolved={"DAI": 1.0}) == ({"HOPR": 20_626 / 230_514}, ["XYZ"])
    # the quote token must be priced first
    assert loader.load(["HOPR"], 1735689600, resolved={}) == ({}, ["HOPR"])
    # a pair holding other tokens than expected is refused
    contracts[dai] = FakeContract({"symbol": "USDC", "decimals": 6})
    assert loader.load(["HOPR"], 1735689600, resolved={"DAI": 1.0}) == ({}, ["HOPR"])
