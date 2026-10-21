"""Shared pytest fixtures. Lives at the repo root so the modules import without installation."""

import pytest

from load0000rs import ethBalance, metaLoad0000rErc20


@pytest.fixture
def chains():
    return [
        {"name": "Testnet", "api": "http://rpc.invalid", "id": 1, "nativeAsset": "ETH",
         "tokens": [{"symbol": "DAI", "address": "0x6B175474E89094C44Da98b954EedeAC495271d0F", "decimals": 18}],
         "metadata": {"blockNumberByTimestamp": {"timestamp": 1735689600, "blockNumber": 12345}}},
        {"name": "Sidechain", "api": ["http://a.invalid", "http://b.invalid"], "id": 2, "nativeAsset": "xDAI"},
    ]


def _entry(**fields):
    return {"version": "0.0.1", "lastRun": "2025-01-01--00-00-00", **fields}


@pytest.fixture
def accounts():
    """Two accounts with latest-block balances loaded on Testnet; Alice also holds DAI."""
    tokenKey = "Single ERC20 balance DAI on Testnet"
    return [
        {"address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045", "index": 0, "mnemonic": "alice",
         "chains": {"Testnet": {
             ethBalance.NAME: _entry(nativeBalance=2.0),
             metaLoad0000rErc20.NAME: {tokenKey: _entry(erc20Balance={"symbol": "DAI", "balance": 100.0})}},
             "Sidechain": {ethBalance.NAME: _entry(nativeBalance=0.0)}}},
        {"address": "0x1Db3439a222C519ab44bb1144fC28167b4Fa6EE6", "index": 1, "mnemonic": "bob",
         "profile": "corporate",
         "chains": {"Testnet": {ethBalance.NAME: _entry(nativeBalance=0.5)}}},
    ]
