"""Web3 connections with failover between the RPC endpoints of a chain.

A chain's "api" field in chains.json is one URL or a list of URLs. Only one endpoint is
used at a time; when a request fails (connection error, timeout, HTTP error, or a JSON-RPC
error response) the provider moves to the next endpoint and retries, wrapping around after
the last one. The position is kept per chain in a module-level cursor so that every
Web3 instance built for the same chain, from any thread, continues from the same endpoint.

Endpoints of one chain may be mixed archive and non-archive: a non-archive endpoint answers
a historical query with an error, which moves the cursor on to the next endpoint.

Always connect with build_web3(chain) rather than Web3(HTTPProvider(url)). It caches one
Web3 per chain and thread; a provider must not be shared between threads because it
changes its endpoint_uri while rotating.
"""

import threading
import time

from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.providers import HTTPProvider

import diagnostics
from utils import is_non_archive_error

_CURSORS = {}  # chain name -> index of the active endpoint
_LOCAL = threading.local()  # .web3s: (chain name, endpoints) -> Web3, one cache per thread


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


def _errorBody(e):
    """The response text behind a requests HTTPError, or "" for any other exception."""
    return getattr(getattr(e, "response", None), "text", None) or ""


class FailoverHTTPProvider(HTTPProvider):
    """HTTPProvider that rotates through `endpoints`, sharing its position via `key`."""

    def __init__(self, endpoints, key, **kwargs):
        self._endpoints = list(endpoints)
        self._key = key
        _CURSORS.setdefault(key, 0)
        super().__init__(self._current_uri(), **kwargs)

    def _current_uri(self):
        return self._endpoints[_CURSORS.get(self._key, 0) % len(self._endpoints)]

    def _rotate(self):
        _CURSORS[self._key] = (_CURSORS.get(self._key, 0) + 1) % len(self._endpoints)
        return self._current_uri()

    def make_request(self, method, params):
        """Try the endpoints in turn until one returns a result.

        Both a transport failure and a JSON-RPC error response move to the next
        endpoint: the read-only calls this tool makes never legitimately fail, so an
        error means the endpoint is unusable (no archive data, API key required, rate
        limited). If every endpoint fails, what is handed to utils.retry decides what
        happens next, in this order:
          1. a transport failure (connection error, HTTP 429/5xx) is raised: an archive
             endpoint that is down right now deserves a retry;
          2. a "not an archive node" response is returned: retry raises it as
             NonArchiveRpcError, which is reported once instead of retried;
          3. any other error response is returned.
        """
        lastError = lastResponse = nonArchiveResponse = None
        for _ in self._endpoints:
            self.endpoint_uri = self._current_uri()
            started = time.time()
            try:
                response = super().make_request(method, params)
            except Exception as e:
                body = _errorBody(e)
                if is_non_archive_error(body):
                    # publicnode refuses archive requests with HTTP 403 and a JSON-RPC body
                    response, reason = {"error": {"code": -32000, "message": body[:200]}}, body[:100]
                    lastResponse, nonArchiveResponse = response, nonArchiveResponse or response
                else:
                    lastError, reason = e, type(e).__name__
            else:
                if "error" not in response:
                    diagnostics.recordCall(self.endpoint_uri, time.time() - started)
                    return response
                lastResponse, reason = response, str(response["error"])[:100]
                if is_non_archive_error(response["error"]):
                    nonArchiveResponse = nonArchiveResponse or response
            diagnostics.recordCall(self.endpoint_uri, time.time() - started, reason)
            if len(self._endpoints) > 1:
                print(f"[rpc failover] {self._key}: {self.endpoint_uri} failed ({reason}) "
                      f"-> switching to {self._rotate()}")
        if lastError is not None:
            raise lastError
        return nonArchiveResponse or lastResponse


def build_web3(chain):
    """A Web3 for `chain` (a dict from chains.json) with endpoint failover.

    The POA middleware is injected so that POA chains (Gnosis, Polygon, BNB, Optimism)
    decode block headers; it is harmless on other chains. The instance is cached per
    thread: building one costs a few milliseconds, which adds up over thousands of tasks.
    """
    endpoints = endpoints_for_chain(chain)
    cache = _LOCAL.__dict__.setdefault("web3s", {})
    key = (chain["name"], tuple(endpoints))
    if key not in cache:
        w3 = Web3(FailoverHTTPProvider(endpoints, chain["name"]))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        cache[key] = w3
    return cache[key]
