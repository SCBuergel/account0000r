import json

import account0000r
from load0000rs import metaLoad0000rErc20
from load0000rs.base import baseLoad0000r


class CountingLoader(baseLoad0000r):
    """Records every (account, chain) it is asked for and returns a fixed value."""

    def __init__(self, name="counter", skip=False, meta=None, fail=False):
        self._name, self.calls, self._fail = name, [], fail
        self._shouldSkipAnalysisIfEntryExists = skip
        self._metaLoad0000r = meta

    def name(self):
        return self._name

    def version(self):
        return "test"

    def analyze(self, account, chain):
        self.calls.append((account, chain["name"]))
        if self._fail:
            raise RuntimeError("boom")
        entry = self.createEmptyAccountEntry()
        entry["value"] = 1
        return entry


def test_accounts_from_secrets_matches_known_test_vectors():
    with open("EXAMPLE-secrets.json") as f:
        accounts = account0000r.accountsFromSecrets(json.load(f))
    assert len(accounts) == 30
    assert accounts[0]["address"] == "0xfc2077CA7F403cBECA41B1B0F62D91B5EA631B5E"
    assert accounts[0] == {"address": accounts[0]["address"], "index": 0,
                           "mnemonic": "plain testvector mnemonic", "chains": {}}
    assert accounts[10]["index"] == 1000
    assert accounts[10]["address"] == "0x58B9112fDE7979E1Fac1C4a6fbec4e4F2FB6662c"
    # deriving again into the same list adds nothing
    with open("EXAMPLE-secrets.json") as f:
        assert len(account0000r.accountsFromSecrets(json.load(f), accounts)) == 30


def test_load_account_metadata_stores_results_and_skips_existing(accounts, chains):
    accounts[0]["address"] = accounts[0]["address"].lower()
    plain = CountingLoader("plain")
    nested = CountingLoader("child", meta=metaLoad0000rErc20.load0000r())
    accounts, errors = account0000r.loadAccountMetadata([plain, nested], accounts, chains, max_workers=2)
    assert errors == []
    assert len(plain.calls) == len(nested.calls) == 4  # 2 accounts x 2 chains
    assert accounts[0]["chains"]["Sidechain"]["plain"]["value"] == 1
    assert accounts[1]["chains"]["Sidechain"][metaLoad0000rErc20.NAME]["child"]["value"] == 1
    # addresses reach the loader checksummed even when stored in lower case
    assert plain.calls[0][0] == "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"

    again = CountingLoader("plain", skip=True)
    account0000r.loadAccountMetadata([again], accounts, chains, max_workers=1)
    assert again.calls == []


def test_load_account_metadata_collects_errors(accounts, chains):
    failing = CountingLoader("fail", fail=True)
    _, errors = account0000r.loadAccountMetadata([failing], accounts[:1], chains[:1], max_workers=1)
    assert len(errors) == 1 and "boom" in errors[0]
    assert "fail" not in accounts[0]["chains"]["Testnet"]


def test_merge_cached_chains(accounts):
    fresh = [{"address": a["address"].lower(), "index": a["index"], "mnemonic": a["mnemonic"]} for a in accounts]
    fresh.append({"address": "0x0000000000000000000000000000000000000001", "index": 9, "mnemonic": "new"})
    assert account0000r.mergeCachedChains(fresh, accounts) == 2
    assert fresh[0]["chains"] == accounts[0]["chains"]
    assert "chains" not in fresh[2]


def test_filter_by_profile(accounts):
    assert [a["mnemonic"] for a in account0000r.filterByProfile(accounts, "personal")] == ["alice"]
    assert [a["mnemonic"] for a in account0000r.filterByProfile(accounts, "corporate")] == ["alice", "bob"]
    assert account0000r.filterByProfile(accounts, None) == accounts


def test_generate_token_loaders_skips_tokens_without_decimals(chains):
    chains[0]["tokens"].append({"symbol": "NEW", "address": "0x0000000000000000000000000000000000000002"})
    loaders, _ = account0000r.generateTokenLoad0000rs(chains, metaLoad0000rErc20.load0000r(), loadChainData=False)
    assert [l.name() for l in loaders] == ["Single ERC20 balance DAI on Testnet"]


def test_generate_token_loaders_loads_metadata_in_parallel_and_skips_failures(chains, monkeypatch):
    import threading
    from load0000rs import singleErc20
    chains[0]["tokens"] += [{"symbol": "A", "address": "0x0000000000000000000000000000000000000002"},
                            {"symbol": "B", "address": "0x0000000000000000000000000000000000000003"},
                            {"symbol": "BAD", "address": "0x0000000000000000000000000000000000000004", "decimals": 6}]
    # all three good tokens must be in loadTokenMetadata at the same time or the barrier breaks
    barrier = threading.Barrier(3, timeout=5)

    def fakeLoadTokenMetadata(self):
        if self._token["symbol"] == "BAD":
            raise RuntimeError("rpc down")
        barrier.wait()
        self._token.setdefault("decimals", 18)

    monkeypatch.setattr(singleErc20.load0000r, "loadTokenMetadata", fakeLoadTokenMetadata)
    loaders, _ = account0000r.generateTokenLoad0000rs(chains, metaLoad0000rErc20.load0000r(), loadChainData=True)
    assert sorted(l._token["symbol"] for l in loaders) == ["A", "B", "DAI"]


def test_write_and_read_json_roundtrip(tmp_path, accounts):
    path = account0000r.writeJson(accounts, str(tmp_path / "x.json"))
    assert account0000r.readJson(path) == accounts


def test_write_json_default_name_uses_the_time_of_the_call(tmp_path, monkeypatch):
    (tmp_path / "data").mkdir()
    monkeypatch.chdir(tmp_path)

    class FakeDatetime:
        stamp = "2025-01-01--00-00-00"

        @classmethod
        def now(cls):
            return cls

        @classmethod
        def strftime(cls, fmt):
            return cls.stamp

    monkeypatch.setattr(account0000r, "datetime", FakeDatetime)
    assert account0000r.writeJson([]) == "data/accounts-2025-01-01--00-00-00.json"
    FakeDatetime.stamp = "2025-06-01--12-00-00"
    assert account0000r.writeJson([]) == "data/accounts-2025-06-01--12-00-00.json"


def test_single_erc20_checks_contract_code_once_per_token(chains, monkeypatch):
    from load0000rs import singleErc20

    class FakeCall:
        def __init__(self, value):
            self.value = value

        def call(self, block_identifier=None):
            return self.value

    class FakeEth:
        def __init__(self, code):
            self.code, self.codeCalls = code, 0

        def get_code(self, address, block_identifier=None):
            self.codeCalls += 1
            return self.code

        def contract(self, address, abi):
            return type("C", (), {"functions": type("F", (), {"balanceOf": lambda a: FakeCall(5 * 10 ** 18)})})

    class FakeWeb3:
        def __init__(self, code):
            self.eth = FakeEth(code)

    token = chains[0]["tokens"][0]
    for code, balance in [(b"\x60", 5.0), (b"", 0)]:
        web3 = FakeWeb3(code)
        monkeypatch.setattr(singleErc20, "build_web3", lambda chain: web3)
        loader = singleErc20.load0000r(True, chains[0], token, metaLoad0000rErc20.load0000r())
        entries = [loader.analyze(a, chains[0]) for a in ("0xA", "0xB", "0xC")]
        assert [e["erc20Balance"]["balance"] for e in entries] == [balance] * 3
        assert web3.eth.codeCalls == 1
