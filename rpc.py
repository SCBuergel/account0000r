"""Web3 connections with failover between the RPC endpoints of a chain.

A chain's "api" field in chains.json is one URL or a list of URLs. Only one endpoint is
used at a time; when a request fails (connection error, timeout, HTTP error, or a JSON-RPC
error response) the provider moves to the next endpoint and retries, wrapping around after
the last one. The position is kept per chain in a module-level cursor so that every
Web3 instance built for the same chain, from any thread, continues from the same endpoint.

Always connect with build_web3(chain) rather than Web3(HTTPProvider(url)).
"""

from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.providers import HTTPProvider

from utils import is_non_archive_error

_CURSORS = {}  # chain name -> index of the active endpoint


def checksum(address):
    """EIP-55 checksummed form of an address (web3 rejects lower-case addresses)."""
    return Web3.to_checksum_address(address)


def endpoints_for_chain(chain):
    """The chain's RPC URLs as a non-empty list."""
    raw = chain.get("api")
    if isinstance(raw, str):
        raw = [raw]
    endpoints = [u for u in (raw or []) if u]
    if not endpoints:
        raise ValueError(f"chain {chain.get('name', '?')!r} has no 'api' endpoint")
    return endpoints


class FailoverHTTPProvider(HTTPProvider):
    """HTTPProvider that rotates through `endpoints`, sharing its position via `key`."""

    def __init__(self, endpoints, key, **kwargs):
        self._endpoints = list(endpoints)
        self._key = key
        _CURSORS.setdefault(key, 0)
        super().__init__(self._current_uri(), **kwargs)

    def _current_uri(self):
        return self._endpoints[_CURSORS[self._key] % len(self._endpoints)]

    def _rotate(self):
        _CURSORS[self._key] = (_CURSORS[self._key] + 1) % len(self._endpoints)
        return self._current_uri()

    def make_request(self, method, params):
        """Try the endpoints in turn until one returns a result.

        Both a transport failure and a JSON-RPC error response move to the next
        endpoint: the read-only calls this tool makes never legitimately fail, so an
        error means the endpoint is unusable (no archive data, API key required, rate
        limited). If every endpoint fails, an error response is returned, or the last
        exception raised, so that utils.retry can classify it. A "not an archive node"
        response is preferred over other errors so that it is reported and not retried.
        """
        lastError = lastResponse = nonArchiveResponse = None
        for _ in self._endpoints:
            self.endpoint_uri = self._current_uri()
            try:
                response = super().make_request(method, params)
            except Exception as e:
                lastError, reason = e, type(e).__name__
            else:
                if "error" not in response:
                    return response
                lastResponse, reason = response, str(response["error"])[:100]
                if is_non_archive_error(response["error"]):
                    nonArchiveResponse = nonArchiveResponse or response
            if len(self._endpoints) > 1:
                print(f"[rpc failover] {self._key}: {self.endpoint_uri} failed ({reason}) "
                      f"-> switching to {self._rotate()}")
        if lastResponse is not None:
            return nonArchiveResponse or lastResponse
        raise lastError


def build_web3(chain):
    """A Web3 for `chain` (a dict from chains.json) with endpoint failover.

    The POA middleware is injected so that POA chains (Gnosis, Polygon, BNB, Optimism)
    decode block headers; it is harmless on other chains.
    """
    w3 = Web3(FailoverHTTPProvider(endpoints_for_chain(chain), chain["name"]))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3
