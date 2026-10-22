"""Small helpers shared by every module: retries, archive-node detection, timestamps."""

import time
from datetime import datetime, timezone

import diagnostics


class NonArchiveRpcError(Exception):
    """The RPC endpoint cannot serve historical state (it is not an archive node)."""


def is_non_archive_error(e):
    msg = str(e).lower()
    return "missing trie node" in msg or ("is not available" in msg and "not found" in msg)


def ts_to_utc(timestamp):
    """Unix timestamp -> 'YYYY-MM-DD HH:MM:SS UTC'."""
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def deep_get(d, *keys, default=None):
    """deep_get(obj, "a", "b") == obj["a"]["b"], or `default` if any key is missing."""
    for key in keys:
        if not isinstance(d, dict) or key not in d:
            return default
        d = d[key]
    return d


def _provider_of(func):
    """The RPC provider behind a bound web3 method, for log messages."""
    try:
        return str(func.__self__.w3.provider)
    except AttributeError:
        return "unknown provider"


def retry(func, *args, max_attempts=10, max_wait=20, **kwargs):
    """Call func(*args, **kwargs); on any exception wait 1, 2, 4, ... seconds (capped at
    max_wait) and try again, up to max_attempts calls in total.

    A "missing trie node" style error is never retried: it means the endpoint is not an
    archive node, and it is raised as NonArchiveRpcError so callers can report it.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if is_non_archive_error(e):
                raise NonArchiveRpcError(_provider_of(func)) from e
            if attempt == max_attempts:
                raise
            wait = min(2 ** (attempt - 1), max_wait)
            print(f"{func} {args} failed ({_provider_of(func)}): {e}. "
                  f"Retrying in {wait}s (attempt {attempt}/{max_attempts}).")
            time.sleep(wait)
            diagnostics.recordBackoff(wait)
