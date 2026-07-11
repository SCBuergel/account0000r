"""Multi-provider RPC failover for chains.

A chain may list several RPC endpoints.  We use one at a time (the "active"
endpoint) and only switch when it errors.  The switch is *sticky and
permanent*: once we move off endpoint N we stay on N+1 until N+1 errors, then
N+2, and so on, wrapping back to the first endpoint after the last one fails.

The active endpoint is tracked per chain in a module-level cursor so that every
Web3 instance built for the same chain — across all loaders — shares the same
position.  Build connections with ``build_web3(chain)`` instead of constructing
``Web3(Web3.HTTPProvider(...))`` directly.

Endpoints are read from the chain's ``"api"`` field, which may be either a
single URL string (backwards compatible) or a list of URL strings.  An
explicit ``"apis"`` list, if present, takes precedence.

    { "name": "Ethereum Main Net", "api": ["https://a", "https://b"], ... }
"""

from web3 import Web3
from web3.providers import HTTPProvider
from web3.middleware import geth_poa_middleware


# chain key -> index of the currently active endpoint (shared across instances)
_CURSORS: dict = {}


def endpoints_for_chain(chain: dict) -> list[str]:
    """Return the ordered list of RPC endpoints configured for *chain*.

    Accepts ``chain["apis"]`` (list), or ``chain["api"]`` as either a single
    URL string or a list of URL strings.
    """
    raw = chain.get("apis")
    if raw is None:
        raw = chain.get("api")
    if raw is None:
        raise ValueError(f"chain {chain.get('name', '?')!r} has no 'api'/'apis' endpoint")
    if isinstance(raw, str):
        return [raw]
    endpoints = [u for u in raw if u]
    if not endpoints:
        raise ValueError(f"chain {chain.get('name', '?')!r} has an empty endpoint list")
    return endpoints


def _chain_key(chain: dict, endpoints: list[str]):
    """Stable identity for a chain's failover cursor."""
    return chain.get("name") or tuple(endpoints)


class FailoverHTTPProvider(HTTPProvider):
    """HTTPProvider that rotates to the next endpoint when a request fails.

    On a transport-level failure (connection error, timeout, HTTP 429/5xx, …)
    the provider advances a shared per-chain cursor to the next endpoint and
    retries.  Within a single request it tries each endpoint at most once; if
    they all fail it re-raises the last error so the caller's retry/backoff
    logic can wait and try again later (resuming from the current endpoint).

    JSON-RPC application errors (e.g. reverts, "missing trie node") are returned
    as normal responses by the underlying provider and therefore do not trigger
    failover.
    """

    def __init__(self, endpoints: list[str], key, **kwargs):
        self._endpoints = list(endpoints)
        self._key = key
        _CURSORS.setdefault(key, 0)
        super().__init__(self._current_uri(), **kwargs)

    def _index(self) -> int:
        return _CURSORS[self._key] % len(self._endpoints)

    def _current_uri(self) -> str:
        return self._endpoints[self._index()]

    def _rotate(self) -> str:
        _CURSORS[self._key] = (_CURSORS[self._key] + 1) % len(self._endpoints)
        return self._current_uri()

    def make_request(self, method, params):
        n = len(self._endpoints)
        last_err = None
        for _ in range(n):
            self.endpoint_uri = self._current_uri()
            try:
                return super().make_request(method, params)
            except Exception as e:
                last_err = e
                if n > 1:
                    failed = self.endpoint_uri
                    new = self._rotate()
                    print(f"[rpc failover] {self._key}: {failed} failed ({type(e).__name__}) "
                          f"-> switching to {new}")
        raise last_err


def build_web3(chain: dict) -> Web3:
    """Return a Web3 connected to *chain* with multi-endpoint failover.

    Drop-in replacement for ``Web3(Web3.HTTPProvider(chain["api"]))``.  Injects
    the POA middleware so POA chains (Polygon, BNB, Gnosis, Optimism, …) decode
    blocks correctly; this is harmless on non-POA chains.
    """
    endpoints = endpoints_for_chain(chain)
    key = _chain_key(chain, endpoints)
    w3 = Web3(FailoverHTTPProvider(endpoints, key))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3
