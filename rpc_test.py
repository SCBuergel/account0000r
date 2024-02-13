import requests
import json
import time
import statistics
import pprint

# List of Ethereum RPC providers
mainnet_rpc_providers = [
    "https://eth.llamarpc.com",
    "https://api.zan.top/node/v1/eth/mainnet/public",
    "https://api.zmok.io/mainnet/oaen6dy8ff6hju9k",
    "https://rpc.flashbots.net",
    "https://rpc.flashbots.net/fast",
    "https://eth.drpc.org",
    "https://api.securerpc.com/v1",
    "https://eth-mainnet.rpcfast.com?api_key=xbhWBI1Wkguk8SNMu1bvvLurPGLXmgwYeC4S6g2H7WdwFigZSmPWVZRxrskEQwIf",
    "https://rpc.lokibuilder.xyz/wallet",
    "https://endpoints.omniatech.io/v1/eth/mainnet/public",
    "https://mainnet.gateway.tenderly.co",
    "https://ethereum.publicnode.com",
    "https://eth.nodeconnect.org",
    "https://1rpc.io/eth",
    "https://gateway.tenderly.co/public/mainnet",
    "https://eth.meowrpc.com",
    "https://rpc.tornadoeth.cash/eth",
    "https://eth.merkle.io",
    "https://rpc.notadegen.com/eth",
    "https://eth-pokt.nodies.app",
    "https://rpc.mevblocker.io/fast",
    "https://uk.rpc.blxrbdn.com",
    "https://virginia.rpc.blxrbdn.com",
    "https://singapore.rpc.blxrbdn.com",
    "https://rpc.builder0x69.io",
    "https://cloudflare-eth.com",
    "https://eth.rpc.blxrbdn.com",
    "https://core.gashawk.io/rpc",
    "https://rpc.payload.de",
    "https://eth-mainnet.public.blastapi.io",
    "https://ethereum.blockpi.network/v1/rpc/public",
    "https://rpc.mevblocker.io/fullprivacy",
    "https://rpc.mevblocker.io",
    "https://rpc.mevblocker.io/noreverts",
    "https://rpc.ankr.com/eth"
]

gnosis_rpc_providers = [
    "https://endpoints.omniatech.io/v1/gnosis/mainnet/public",
    "https://rpc.gnosischain.com",
    "https://gnosis.publicnode.com",
    "https://gnosis.oat.farm",
    "https://gnosis.drpc.org",
    "https://rpc.ap-southeast-1.gateway.fm/v4/gnosis/non-archival/mainnet",
    "https://rpc.gnosis.gateway.fm",
    "https://gnosis-pokt.nodies.app",
    "https://gnosis.blockpi.network/v1/rpc/public",
    "https://gnosis-mainnet.public.blastapi.io",
    "https://rpc.ankr.com/gnosis",
    "https://1rpc.io/gnosis",
    "https://rpc.tornadoeth.cash/gnosis"
]

optimism_rpc_providers = [
    "https://optimism.llamarpc.com",
    "https://endpoints.omniatech.io/v1/op/mainnet/public",
    "https://mainnet.optimism.io",
    "https://gateway.tenderly.co/public/optimism",
    "https://optimism.blockpi.network/v1/rpc/public",
    "https://optimism.drpc.org",
    "https://optimism.gateway.tenderly.co",
    "https://optimism.meowrpc.com",
    "https://rpc.optimism.gateway.fm",
    "https://optimism-mainnet.public.blastapi.io",
    "https://rpc.tornadoeth.cash/optimism",
    "https://api.zan.top/node/v1/opt/mainnet/public",
    "https://optimism.api.onfinality.io/public",
    "https://1rpc.io/op",
    "https://op-pokt.nodies.app",
    "https://rpc.ankr.com/optimism",
    "https://optimism.publicnode.com"
]

arbitrum_rpc_providers = [
    "https://arbitrum.llamarpc.com",
    "https://endpoints.omniatech.io/v1/arbitrum/one/public",
    "https://rpc.tornadoeth.cash/arbitrum",
    "https://arb-mainnet-public.unifra.io",
    "https://arbitrum-one.public.blastapi.io",
    "https://arb1.arbitrum.io/rpc",
    "https://arb-pokt.nodies.app",
    "https://arbitrum.blockpi.network/v1/rpc/public",
    "https://arbitrum.drpc.org",
    "https://rpc.arb1.arbitrum.gateway.fm",
    "https://arbitrum-one.publicnode.com",
    "https://1rpc.io/arb",
    "https://rpc.ankr.com/arbitrum",
    "https://api.zan.top/node/v1/arb/one/public",
    "https://arbitrum.meowrpc.com"
]

polygon_rpc_providers = [
    "https://polygon.llamarpc.com",
    "https://1rpc.io/matic",
    "https://rpc-mainnet.matic.quiknode.pro",
    "https://polygon.drpc.org",
    "https://endpoints.omniatech.io/v1/matic/mainnet/public",
    "https://polygon-bor.publicnode.com",
    "https://polygon.rpc.blxrbdn.com",
    "https://polygon-mainnet.rpcfast.com?api_key=xbhWBI1Wkguk8SNMu1bvvLurPGLXmgwYeC4S6g2H7WdwFigZSmPWVZRxrskEQwIf",
    "https://polygon-pokt.nodies.app",
    "https://polygon.meowrpc.com",
    "https://polygon-rpc.com",
    "https://polygon-mainnet.public.blastapi.io",
    "https://rpc-mainnet.maticvigil.com",
    "https://polygon.blockpi.network/v1/rpc/public",
    "https://polygon.gateway.tenderly.co",
    "https://rpc.ankr.com/polygon",
    "https://gateway.tenderly.co/public/polygon",
    "https://rpc.tornadoeth.cash/polygon",
    "https://polygon.api.onfinality.io/public"
]

bnb_rpc_providers = [
    "https://binance.llamarpc.com",
    "https://endpoints.omniatech.io/v1/bsc/mainnet/public",
    "https://rpc.polysplit.cloud/v1/chain/56",
    "https://bsc-mainnet.nodereal.io/v1/64a9df0874fb4a93b9d0a3849de012d3",
    "https://binance.nodereal.io",
    "https://bsc.drpc.org",
    "https://bsc.rpc.blxrbdn.com",
    "https://bsc.publicnode.com",
    "https://1rpc.io/bnb",
    "https://bsc.meowrpc.com",
    "https://bsc-dataseed4.defibit.io",
    "https://bsc-dataseed1.defibit.io",
    "https://bsc-dataseed3.defibit.io",
    "https://bsc-dataseed.bnbchain.org",
    "https://bsc-dataseed2.ninicoin.io",
    "https://bsc-dataseed3.ninicoin.io",
    "https://bsc-dataseed4.ninicoin.io",
    "https://bsc-dataseed2.bnbchain.org",
    "https://bsc-dataseed3.bnbchain.org",
    "https://bsc-dataseed4.bnbchain.org",
    "https://api.zan.top/node/v1/bsc/mainnet/public",
    "https://bsc-dataseed1.bnbchain.org",
    "https://bsc-dataseed1.ninicoin.io",
    "https://bsc-pokt.nodies.app",
    "https://bsc-mainnet.rpcfast.com?api_key=xbhWBI1Wkguk8SNMu1bvvLurPGLXmgwYeC4S6g2H7WdwFigZSmPWVZRxrskEQwIf",
    "https://bsc-mainnet.public.blastapi.io",
    "https://bsc-dataseed2.defibit.io",
    "https://rpc-bsc.48.club",
    "https://koge-rpc-bsc.48.club",
    "https://bsc.blockpi.network/v1/rpc/public",
    "https://rpc.ankr.com/bsc",
    "https://bscrpc.com",
    "https://rpc.tornadoeth.cash/bsc",
    "https://bnb.api.onfinality.io/public"
]

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


# Check each RPC provider and prin0t if it's an archive node
providers = {
        "mainnet": mainnet_rpc_providers,
        "gnosis": gnosis_rpc_providers,
        "optimism": optimism_rpc_providers,
        "arbitrum": arbitrum_rpc_providers,
        "polygon": polygon_rpc_providers,
        "Binance Chain": bnb_rpc_providers
        }

results = {}
for chain in providers.keys():
    data = []
    attempts_per_provider = 20
    for rpc in providers[chain]:
        latencies = test_rpc(rpc, num_requests=attempts_per_provider)
        count = len(latencies) / attempts_per_provider * 100
        median = statistics.median(latencies) if len(latencies) > 0 else 0.0
        stdev = statistics.stdev(latencies) if len(latencies) > 1 else 0.0
        data.append([rpc, count, median, stdev])
        if len(latencies) > 0:
            print(f"{rpc} is an archive node. Responses: {float(count):.2f}%. Median latency: {median:.3f} +/- {stdev:.3f}s")
        else:
            print(f"{rpc} is not an archive node or is unreachable.")


    data = sorted(data, key=lambda x: (-x[1], x[2], x[0]))
    data = [row[:1] + ["{:.2f}".format(row[1])] + ["{:.3f}".format(row[2])] + ["{:.3f}".format(row[3])] for row in data]
    data.insert(0, ["RPC provider", "success rate [%]", "median latency [s]", "stdev [s]"])
    results[chain] = data

for chain in providers.keys():
    data = results[chain]
    col_widths = [max(len(str(cell)) for cell in column) for column in zip(*data)]

    # Print the table
    print(f"\n{chain}")
    for row in data:
        print(" | ".join(f"{cell:>{col_widths[i]}}" for i, cell in enumerate(row)))

