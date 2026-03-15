import time
from datetime import datetime, timezone


class NonArchiveRpcError(Exception):
    """Raised when an RPC provider does not support archive/historical data."""
    pass


def ts_to_utc(timestamp: int) -> str:
    """Format a Unix timestamp as a human-readable UTC string."""
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _is_non_archive_error(e):
    msg = str(e).lower()
    return "missing trie node" in msg or ("is not available" in msg and "not found" in msg)


def deep_get(d, *keys, default=None):
    """Safely traverse nested dicts: deep_get(obj, "a", "b", "c", default=0)"""
    for key in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(key, default)
        if d is default:
            return default
    return d


def check_archive(chains, chain_name):
    """Test whether the RPC provider for *chain_name* has archive capabilities.

    Probes by requesting the ETH balance of the zero address at block 1 — a
    query that only archive nodes can answer.  Prints the result and returns
    True if the node is an archive node, False otherwise.

    Parameters
    ----------
    chains : list[dict]
        Chain list as loaded from chains.json.
    chain_name : str
        Value of the "name" field identifying the chain to test.
    """
    from web3 import Web3

    chain = next((c for c in chains if c["name"] == chain_name), None)
    if chain is None:
        print(f"check_archive: chain '{chain_name}' not found in chains list")
        return False

    w3 = Web3(Web3.HTTPProvider(chain["api"]))
    try:
        w3.eth.get_balance("0x0000000000000000000000000000000000000000", 1)
        print(f"[archive] {chain_name} ({chain['api']}): archive node ✓")
        return True
    except Exception as e:
        if _is_non_archive_error(e):
            print(f"[archive] {chain_name} ({chain['api']}): NOT an archive node")
        else:
            print(f"[archive] {chain_name} ({chain['api']}): unexpected error — {e}")
        return False


def _exponential_backoff(func, *args, max_wait=20, max_attempts=10, **kwargs):
    """calls any function with any parameters with an exponential backoff on any exception
    You can use this function for e.g. _exponential_backoff(web3.eth.get_block, 1234)
    """

    attempt = 0
    wait_time = 1  # Initial wait time of 1 second

    while True:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if _is_non_archive_error(e):
                try:
                    provider = str(func.__self__.w3.provider)
                except AttributeError:
                    provider = "unknown provider"
                raise NonArchiveRpcError(provider) from e
            try:
                provider_info = f" (provider: {func.__self__.w3.provider})"
            except AttributeError:
                provider_info = ""
            print(f"Function call {func} with {args} failed: {e}{provider_info}. Retrying in {wait_time}s.")
            time.sleep(wait_time)
            attempt += 1
            wait_time = min(2 ** attempt, max_wait)

            if attempt > max_attempts:
                print(f"attempted to call more than {max_attempts} times. Aborting.")
                raise
