"""Benchmark every RPC endpoint listed in a chains file.

    python rpc_test.py [data/chains.json] [--requests 10]

Each endpoint is asked for the balance of the zero address at block 1, which only an
archive node can answer, so the success rate also tells whether the endpoint can serve
accounting.py step 4. Use the result to reorder or replace the "api" entries.
"""

import argparse
import json
import statistics
import time

import requests

from rpc import endpoints_for_chain


def probe(url, requestsPerEndpoint, timeout=10):
    """Latencies in seconds of the successful requests to `url`."""
    payload = {"jsonrpc": "2.0", "method": "eth_getBalance", "id": 1,
               "params": ["0x0000000000000000000000000000000000000000", "0x1"]}
    latencies = []
    for _ in range(requestsPerEndpoint):
        start = time.time()
        try:
            response = requests.post(url, json=payload, timeout=timeout)
            if response.status_code == 200 and "result" in response.json():
                latencies.append(time.time() - start)
        except Exception:
            pass
    return latencies


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("chains", nargs="?", default="data/chains.json")
    parser.add_argument("--requests", type=int, default=10, help="requests per endpoint (default 10)")
    args = parser.parse_args()
    with open(args.chains) as f:
        chains = json.load(f)
    for chain in chains:
        rows = []
        for url in endpoints_for_chain(chain):
            latencies = probe(url, args.requests)
            rows.append((url, 100 * len(latencies) / args.requests,
                         statistics.median(latencies) if latencies else float("inf"),
                         statistics.stdev(latencies) if len(latencies) > 1 else 0.0))
        rows.sort(key=lambda r: (-r[1], r[2]))
        width = max(len(r[0]) for r in rows)
        print(f"\n{chain['name']}\n{'endpoint':<{width}}  success  median  stdev")
        for url, success, median, stdev in rows:
            print(f"{url:<{width}}  {success:6.0f}%  {median:6.3f}  {stdev:5.3f}")


if __name__ == "__main__":
    main()
