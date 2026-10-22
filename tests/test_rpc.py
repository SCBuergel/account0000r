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
    rpc._LOCAL.__dict__.clear()  # cached Web3 instances of earlier tests
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


def test_failover_when_all_endpoints_fail_prefers_transient_then_archive_errors(fakeRpc, chains):
    behaviour, _ = fakeRpc
    nonArchive = {"error": {"code": -32000, "message": "missing trie node"}}
    dead = {"error": {"code": -32000, "message": "Unauthorized"}}

    # a transport failure is raised so that retry tries again: that endpoint may be back
    behaviour["http://a.invalid"] = nonArchive
    behaviour["http://b.invalid"] = ConnectionError("down")
    with pytest.raises(ConnectionError):
        rpc.build_web3(chains[1]).provider.make_request("x", [])

    # otherwise a non-archive answer wins over a dead endpoint, whichever came first
    behaviour["http://b.invalid"] = dead
    for cursor in (0, 1):
        rpc._CURSORS["Sidechain"] = cursor
        assert rpc.build_web3(chains[1]).provider.make_request("x", []) == nonArchive

    behaviour["http://a.invalid"] = dead
    assert rpc.build_web3(chains[1]).provider.make_request("x", []) == dead


def test_http_error_carrying_an_archive_refusal_counts_as_non_archive(fakeRpc, chains):
    import requests
    behaviour, _ = fakeRpc
    refusal = requests.Response()
    refusal.status_code = 403
    refusal._content = b'{"jsonrpc":"2.0","error":{"code":-32602,"message":"Archive requests require a personal token"}}'
    behaviour["http://rpc.invalid"] = requests.HTTPError("403 Client Error", response=refusal)
    response = rpc.build_web3(chains[0]).provider.make_request("x", [])
    assert "Archive requests require" in response["error"]["message"]


def test_build_web3_caches_per_thread(chains):
    import threading
    first = rpc.build_web3(chains[0])
    assert rpc.build_web3(chains[0]) is first
    assert rpc.build_web3(chains[1]) is not first
    fromThread = []
    t = threading.Thread(target=lambda: fromThread.append(rpc.build_web3(chains[0])))
    t.start()
    t.join()
    assert fromThread[0] is not first
