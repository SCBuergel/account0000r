import requests
import json
import time
import statistics
import pprint

# List of Ethereum RPC providers
mainnet_rpc_providers = [
    "https://eth.llamarpc.com",
    "https://endpoints.omniatech.io/v1/eth/mainnet/public",
    "https://rpc.ankr.com/eth",
    "https://go.getblock.io/d7dab8149ec04390aaa923ff2768f914",
    "https://eth-mainnet.nodereal.io/v1/1659dfb40aa24bbb8153a677b98064d7",
    "https://ethereum.publicnode.com",
    "wss://ethereum.publicnode.com",
    "https://1rpc.io/eth",
    "https://rpc.builder0x69.io",
    "https://rpc.mevblocker.io",
    "https://rpc.flashbots.net",
    "https://virginia.rpc.blxrbdn.com",
    "https://uk.rpc.blxrbdn.com",
    "https://singapore.rpc.blxrbdn.com",
    "https://eth.rpc.blxrbdn.com",
    "https://cloudflare-eth.com",
    "https://eth-mainnet.public.blastapi.io",
    "https://api.securerpc.com/v1",
    "https://openapi.bitstack.com/v1/wNFxbiJyQsSeLrX8RRCHi7NpRxrlErZk/DjShIqLishPCTB9HiMkPHXjUM9CNM9Na/ETH/mainnet",
    "https://eth-pokt.nodies.app",
    "https://eth-mainnet-public.unifra.io",
    "https://ethereum.blockpi.network/v1/rpc/public",
    "https://rpc.payload.de",
    "https://api.zmok.io/mainnet/oaen6dy8ff6hju9k",
    "https://eth-mainnet.g.alchemy.com/v2/demo",
    "https://eth.api.onfinality.io/public",
    "https://core.gashawk.io/rpc",
    "https://mainnet.eth.cloud.ava.do",
    "https://ethereumnodelight.app.runonflux.io",
    "https://eth-mainnet.rpcfast.com?api_key=xbhWBI1Wkguk8SNMu1bvvLurPGLXmgwYeC4S6g2H7WdwFigZSmPWVZRxrskEQwIf",
    "https://main-light.eth.linkpool.io",
    "https://rpc.eth.gateway.fm",
    "https://rpc.chain49.com/ethereum?api_key=14d1a8b86d8a4b4797938332394203dc",
    "https://eth.meowrpc.com",
    "https://eth.drpc.org",
    "https://mainnet.gateway.tenderly.co",
    "https://rpc.tenderly.co/fork/c63af728-a183-4cfb-b24e-a92801463484",
    "https://gateway.tenderly.co/public/mainnet",
    "https://api.zan.top/node/v1/eth/mainnet/public",
    "https://eth-mainnet.diamondswap.org/rpc",
    "https://rpc.notadegen.com/eth",
    "https://eth.merkle.io",
    "https://rpc.lokibuilder.xyz/wallet",
    "https://services.tokenview.io/vipapi/nodeservice/eth?apikey=qVHq2o6jpaakcw3lRstl",
    "https://eth.nodeconnect.org",
    "https://api.mycryptoapi.com/eth",
    "wss://mainnet.gateway.tenderly.co",
    "https://rpc.blocknative.com/boost",
    "https://rpc.flashbots.net/fast",
    "https://rpc.mevblocker.io/fast",
    "https://rpc.mevblocker.io/noreverts",
    "https://rpc.mevblocker.io/fullprivacy"
]
#"""

# Function to check if an RPC provider is an archive node
def test_rpc(rpc_url, block="0xf4240", num_requests=20, address="0x0000000000000000000000000000000000000000"):

    # JSON-RPC request payload
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [address, block],
        "id": 1
    }

    headers = {
        "Content-Type": "application/json"
    }

    latencies = []

    for _ in range(num_requests):
        try:
            start_time = time.time()
            response = requests.post(rpc_url, json=payload, headers=headers)
            latency = time.time() - start_time

            if response.status_code == 200 and "result" in response.json():
                latencies.append(latency)
                print(f"{rpc} in {latency:.3f}s: {response.json()}")
            else:
                print(f"{rpc} failed with code {response.status_code}: {response.json()}")
        except requests.exceptions.RequestException as e:
            print(f"Error querying {rpc_url}: {e}")

    # Calculate average latency
    return latencies


# Check each RPC provider and print if it's an archive node
data = []
for rpc in mainnet_rpc_providers:
    latencies = test_rpc(rpc, block="latest", num_requests=100)
    count = len(latencies)
    median = f"{statistics.median(latencies) if count > 0 else 0.0:.3f}"
    stdev = f"{statistics.stdev(latencies) if count > 0 else 0.0:.3f}"
    data.append([rpc, count, median, stdev])
    if len(latencies) > 0:
        print(f"{rpc} is an archive node. Responses: {count}. Median latency: {median} +/- {stdev}s")
    else:
        print(f"{rpc} is not an archive node or is unreachable.")


data = sorted(data, key=lambda x: (-x[1], x[2], x[0]))
data.insert(0, ["RPC provider", "success rate [%]", "avg latency [s]", "stdev [s]"])
col_widths = [max(len(str(cell)) for cell in column) for column in zip(*data)]

# Print the table
for row in data:
    print(" | ".join(f"{cell:>{col_widths[i]}}" for i, cell in enumerate(row)))

