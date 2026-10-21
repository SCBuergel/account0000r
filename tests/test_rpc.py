import pytest
from web3.providers import HTTPProvider

import rpc


def test_endpoints_for_chain_accepts_string_or_list(chains):
    assert rpc.endpoints_for_chain(chains[0]) == ["http://rpc.invalid"]
    assert rpc.endpoints_for_chain(chains[1]) == ["http://a.invalid", "http://b.invalid"]
    with pytest.raises(ValueError):
        rpc.endpoints_for_chain({"name": "x", "api": []})


@pytest.fixture
def fakeRpc(monkeypatch):
    """Replace the HTTP layer: `behaviour` maps an endpoint to an exception, an error
    response, or nothing (success). Records the endpoints tried."""
    rpc._CURSORS.clear()
    behaviour, seen = {}, []

    def fake_request(self, method, params):
        seen.append(self.endpoint_uri)
        outcome = behaviour.get(self.endpoint_uri)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome or {"result": self.endpoint_uri}

    monkeypatch.setattr(HTTPProvider, "make_request", fake_request)
    return behaviour, seen


def test_failover_rotates_on_exceptions_and_error_responses(fakeRpc, chains):
    behaviour, seen = fakeRpc
    behaviour["http://a.invalid"] = ConnectionError("down")
    w3 = rpc.build_web3(chains[1])
    assert w3.provider.make_request("eth_blockNumber", []) == {"result": "http://b.invalid"}
    assert seen == ["http://a.invalid", "http://b.invalid"]
    # a new instance for the same chain starts at the endpoint that worked
    assert rpc.build_web3(chains[1]).provider.make_request("x", []) == {"result": "http://b.invalid"}

    behaviour["http://b.invalid"] = {"error": {"code": -32000, "message": "API key required"}}
    behaviour["http://a.invalid"] = None
    assert w3.provider.make_request("x", []) == {"result": "http://a.invalid"}


def test_failover_returns_last_error_when_all_endpoints_fail(fakeRpc, chains):
    behaviour, _ = fakeRpc
    nonArchive = {"error": {"code": -32000, "message": "missing trie node"}}
    behaviour["http://a.invalid"] = nonArchive
    behaviour["http://b.invalid"] = ConnectionError("down")
    assert rpc.build_web3(chains[1]).provider.make_request("x", []) == nonArchive

    # a dead endpoint's error must not hide the archive error of another endpoint
    behaviour["http://b.invalid"] = {"error": {"code": -32000, "message": "Unauthorized"}}
    rpc._CURSORS["Sidechain"] = 0  # archive error first, dead endpoint last
    assert rpc.build_web3(chains[1]).provider.make_request("x", []) == nonArchive

    behaviour["http://a.invalid"] = ConnectionError("down")
    behaviour["http://b.invalid"] = ConnectionError("down")
    with pytest.raises(ConnectionError):
        rpc.build_web3(chains[1]).provider.make_request("x", [])
