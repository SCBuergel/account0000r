RPC performance measurements done via `python rpc-test.py` from Germany on 2024-02-13:

## mainnet
```
                                                                                            RPC provider | success rate [%] | median latency [s] | stdev [s]
                                                                     https://rpc.mevblocker.io/noreverts |           100.00 |              0.142 |     0.013
                                                                   https://rpc.mevblocker.io/fullprivacy |           100.00 |              0.143 |     0.008
                                                                               https://rpc.mevblocker.io |           100.00 |              0.144 |     0.007
                                                                                https://rpc.ankr.com/eth |           100.00 |              0.145 |     0.190
                                                                           https://rpc.notadegen.com/eth |           100.00 |              0.148 |     0.130
                                                                              https://rpc.builder0x69.io |           100.00 |              0.180 |     0.070
                                                                             https://eth-pokt.nodies.app |           100.00 |              0.199 |     0.034
                                                                          https://rpc.mevblocker.io/fast |           100.00 |              0.202 |     0.031
                                                                             https://eth.nodeconnect.org |           100.00 |              0.293 |     0.065
                                                                                    https://eth.drpc.org |           100.00 |              0.294 |     0.158
                                                                                https://eth.llamarpc.com |           100.00 |              0.409 |     0.063
                                                                          https://rpc.flashbots.net/fast |           100.00 |              0.411 |     0.338
                                                                               https://rpc.flashbots.net |           100.00 |              0.413 |     0.247
                                                                                   https://eth.merkle.io |           100.00 |              0.433 |     0.098
                                                                              https://cloudflare-eth.com |           100.00 |              0.446 |     0.097
                                                                             https://core.gashawk.io/rpc |           100.00 |              0.678 |     0.109
                                                                                     https://1rpc.io/eth |           100.00 |              1.002 |     0.364
                                                                         https://rpc.tornadoeth.cash/eth |           100.00 |              1.220 |     0.617
                                                    https://endpoints.omniatech.io/v1/eth/mainnet/public |            70.00 |              2.341 |     2.472
                                                                     https://mainnet.gateway.tenderly.co |            65.00 |              0.107 |     0.015
                                                              https://gateway.tenderly.co/public/mainnet |            65.00 |              0.108 |     0.012
                                                                  https://eth-mainnet.public.blastapi.io |            60.00 |              0.170 |     0.100
                                                          https://ethereum.blockpi.network/v1/rpc/public |            55.00 |              0.114 |     0.013
                                                                            https://api.securerpc.com/v1 |             0.00 |              0.000 |     0.000
                                                          https://api.zan.top/node/v1/eth/mainnet/public |             0.00 |              0.000 |     0.000
                                                            https://api.zmok.io/mainnet/oaen6dy8ff6hju9k |             0.00 |              0.000 |     0.000
https://eth-mainnet.rpcfast.com?api_key=xbhWBI1Wkguk8SNMu1bvvLurPGLXmgwYeC4S6g2H7WdwFigZSmPWVZRxrskEQwIf |             0.00 |              0.000 |     0.000
                                                                                 https://eth.meowrpc.com |             0.00 |              0.000 |     0.000
                                                                             https://eth.rpc.blxrbdn.com |             0.00 |              0.000 |     0.000
                                                                         https://ethereum.publicnode.com |             0.00 |              0.000 |     0.000
                                                                      https://rpc.lokibuilder.xyz/wallet |             0.00 |              0.000 |     0.000
                                                                                  https://rpc.payload.de |             0.00 |              0.000 |     0.000
                                                                       https://singapore.rpc.blxrbdn.com |             0.00 |              0.000 |     0.000
                                                                              https://uk.rpc.blxrbdn.com |             0.00 |              0.000 |     0.000
                                                                        https://virginia.rpc.blxrbdn.com |             0.00 |              0.000 |     0.000
```

## gnosis
```
                                                        RPC provider | success rate [%] | median latency [s] | stdev [s]
                                         https://rpc.ankr.com/gnosis |           100.00 |              0.144 |     0.061
                                  https://rpc.tornadoeth.cash/gnosis |           100.00 |              1.945 |     0.572
             https://endpoints.omniatech.io/v1/gnosis/mainnet/public |            80.00 |              3.760 |     1.204
                        https://gnosis.blockpi.network/v1/rpc/public |            75.00 |              0.117 |     0.024
                           https://gnosis-mainnet.public.blastapi.io |            60.00 |              0.426 |     0.107
                                             https://gnosis.drpc.org |            55.00 |              0.366 |     0.215
                                              https://1rpc.io/gnosis |             0.00 |              0.000 |     0.000
                                      https://gnosis-pokt.nodies.app |             0.00 |              0.000 |     0.000
                                             https://gnosis.oat.farm |             0.00 |              0.000 |     0.000
                                       https://gnosis.publicnode.com |             0.00 |              0.000 |     0.000
https://rpc.ap-southeast-1.gateway.fm/v4/gnosis/non-archival/mainnet |             0.00 |              0.000 |     0.000
                                       https://rpc.gnosis.gateway.fm |             0.00 |              0.000 |     0.000
                                         https://rpc.gnosischain.com |             0.00 |              0.000 |     0.000
```

## optimism
```
                                       RPC provider | success rate [%] | median latency [s] | stdev [s]
                        https://mainnet.optimism.io |           100.00 |              0.123 |     0.014
                      https://rpc.ankr.com/optimism |           100.00 |              0.147 |     0.055
                          https://optimism.drpc.org |           100.00 |              0.252 |     0.461
               https://rpc.tornadoeth.cash/optimism |           100.00 |              0.469 |     0.369
                                 https://1rpc.io/op |           100.00 |              1.228 |     0.234
https://endpoints.omniatech.io/v1/op/mainnet/public |            85.00 |              1.740 |     1.126
               https://optimism.gateway.tenderly.co |            65.00 |              0.111 |     0.013
     https://optimism.blockpi.network/v1/rpc/public |            65.00 |              0.119 |     0.012
        https://gateway.tenderly.co/public/optimism |            60.00 |              0.109 |     0.027
        https://optimism-mainnet.public.blastapi.io |            15.00 |              0.519 |     0.043
          https://optimism.api.onfinality.io/public |            15.00 |              0.916 |     0.058
     https://api.zan.top/node/v1/opt/mainnet/public |             0.00 |              0.000 |     0.000
                         https://op-pokt.nodies.app |             0.00 |              0.000 |     0.000
                      https://optimism.llamarpc.com |             0.00 |              0.000 |     0.000
                       https://optimism.meowrpc.com |             0.00 |              0.000 |     0.000
                    https://optimism.publicnode.com |             0.00 |              0.000 |     0.000
                    https://rpc.optimism.gateway.fm |             0.00 |              0.000 |     0.000
```

## arbitrum
```
                                         RPC provider | success rate [%] | median latency [s] | stdev [s]
                        https://rpc.ankr.com/arbitrum |           100.00 |              0.147 |     0.062
                 https://rpc.arb1.arbitrum.gateway.fm |           100.00 |              0.264 |     0.166
                 https://rpc.tornadoeth.cash/arbitrum |           100.00 |              0.410 |     0.130
       https://arbitrum.blockpi.network/v1/rpc/public |            95.00 |              0.132 |     0.045
https://endpoints.omniatech.io/v1/arbitrum/one/public |            90.00 |              2.404 |     1.337
                 https://arb-mainnet-public.unifra.io |            70.00 |              0.319 |     0.127
              https://arbitrum-one.public.blastapi.io |            55.00 |              0.403 |     0.686
                                  https://1rpc.io/arb |             0.00 |              0.000 |     0.000
           https://api.zan.top/node/v1/arb/one/public |             0.00 |              0.000 |     0.000
                          https://arb-pokt.nodies.app |             0.00 |              0.000 |     0.000
                         https://arb1.arbitrum.io/rpc |             0.00 |              0.000 |     0.000
                  https://arbitrum-one.publicnode.com |             0.00 |              0.000 |     0.000
                            https://arbitrum.drpc.org |             0.00 |              0.000 |     0.000
                        https://arbitrum.llamarpc.com |             0.00 |              0.000 |     0.000
                         https://arbitrum.meowrpc.com |             0.00 |              0.000 |     0.000
```

## polygon
```
                                                                                                RPC provider | success rate [%] | median latency [s] | stdev [s]
                                                                                     https://polygon-rpc.com |           100.00 |              0.131 |     0.059
                                                                                https://rpc.ankr.com/polygon |           100.00 |              0.140 |     0.014
                                                                         https://rpc.tornadoeth.cash/polygon |           100.00 |              0.562 |     0.204
                                                                                       https://1rpc.io/matic |           100.00 |              1.058 |     0.284
                                                      https://endpoints.omniatech.io/v1/matic/mainnet/public |            85.00 |              2.175 |     1.477
                                                                                    https://polygon.drpc.org |            75.00 |              0.184 |     0.224
                                                                         https://polygon.gateway.tenderly.co |            65.00 |              0.110 |     0.015
                                                                  https://gateway.tenderly.co/public/polygon |            60.00 |              0.111 |     0.008
                                                               https://polygon.blockpi.network/v1/rpc/public |            55.00 |              0.121 |     0.010
                                                                                https://polygon.llamarpc.com |            20.00 |              0.752 |     0.142
                                                                    https://polygon.api.onfinality.io/public |            15.00 |              0.648 |     0.085
                                                                          https://polygon-bor.publicnode.com |             0.00 |              0.000 |     0.000
                                                                  https://polygon-mainnet.public.blastapi.io |             0.00 |              0.000 |     0.000
https://polygon-mainnet.rpcfast.com?api_key=xbhWBI1Wkguk8SNMu1bvvLurPGLXmgwYeC4S6g2H7WdwFigZSmPWVZRxrskEQwIf |             0.00 |              0.000 |     0.000
                                                                             https://polygon-pokt.nodies.app |             0.00 |              0.000 |     0.000
                                                                                 https://polygon.meowrpc.com |             0.00 |              0.000 |     0.000
                                                                             https://polygon.rpc.blxrbdn.com |             0.00 |              0.000 |     0.000
                                                                      https://rpc-mainnet.matic.quiknode.pro |             0.00 |              0.000 |     0.000
                                                                          https://rpc-mainnet.maticvigil.com |             0.00 |              0.000 |     0.000
```

## binance chain
```
                                                                                            RPC provider | success rate [%] | median latency [s] | stdev [s]
                                                                                      https://bscrpc.com |           100.00 |              0.124 |     0.021
                                                                                https://rpc.ankr.com/bsc |           100.00 |              0.134 |     0.090
                                     https://bsc-mainnet.nodereal.io/v1/64a9df0874fb4a93b9d0a3849de012d3 |           100.00 |              0.174 |     0.011
                                                                            https://binance.llamarpc.com |           100.00 |              0.400 |     0.084
                                                                         https://rpc.tornadoeth.cash/bsc |           100.00 |              0.409 |     0.088
                                                    https://endpoints.omniatech.io/v1/bsc/mainnet/public |            75.00 |              1.820 |     1.617
                                                                  https://bsc-mainnet.public.blastapi.io |            70.00 |              0.170 |     0.106
                                                               https://bsc.blockpi.network/v1/rpc/public |            55.00 |              0.117 |     0.016
                                                                    https://bnb.api.onfinality.io/public |            15.00 |              0.822 |     0.213
                                                                                     https://1rpc.io/bnb |             0.00 |              0.000 |     0.000
                                                          https://api.zan.top/node/v1/bsc/mainnet/public |             0.00 |              0.000 |     0.000
                                                                             https://binance.nodereal.io |             0.00 |              0.000 |     0.000
                                                                       https://bsc-dataseed.bnbchain.org |             0.00 |              0.000 |     0.000
                                                                      https://bsc-dataseed1.bnbchain.org |             0.00 |              0.000 |     0.000
                                                                        https://bsc-dataseed1.defibit.io |             0.00 |              0.000 |     0.000
                                                                       https://bsc-dataseed1.ninicoin.io |             0.00 |              0.000 |     0.000
                                                                      https://bsc-dataseed2.bnbchain.org |             0.00 |              0.000 |     0.000
                                                                        https://bsc-dataseed2.defibit.io |             0.00 |              0.000 |     0.000
                                                                       https://bsc-dataseed2.ninicoin.io |             0.00 |              0.000 |     0.000
                                                                      https://bsc-dataseed3.bnbchain.org |             0.00 |              0.000 |     0.000
                                                                        https://bsc-dataseed3.defibit.io |             0.00 |              0.000 |     0.000
                                                                       https://bsc-dataseed3.ninicoin.io |             0.00 |              0.000 |     0.000
                                                                      https://bsc-dataseed4.bnbchain.org |             0.00 |              0.000 |     0.000
                                                                        https://bsc-dataseed4.defibit.io |             0.00 |              0.000 |     0.000
                                                                       https://bsc-dataseed4.ninicoin.io |             0.00 |              0.000 |     0.000
https://bsc-mainnet.rpcfast.com?api_key=xbhWBI1Wkguk8SNMu1bvvLurPGLXmgwYeC4S6g2H7WdwFigZSmPWVZRxrskEQwIf |             0.00 |              0.000 |     0.000
                                                                             https://bsc-pokt.nodies.app |             0.00 |              0.000 |     0.000
                                                                                    https://bsc.drpc.org |             0.00 |              0.000 |     0.000
                                                                                 https://bsc.meowrpc.com |             0.00 |              0.000 |     0.000
                                                                              https://bsc.publicnode.com |             0.00 |              0.000 |     0.000
                                                                             https://bsc.rpc.blxrbdn.com |             0.00 |              0.000 |     0.000
                                                                            https://koge-rpc-bsc.48.club |             0.00 |              0.000 |     0.000
                                                                                 https://rpc-bsc.48.club |             0.00 |              0.000 |     0.000
                                                                 https://rpc.polysplit.cloud/v1/chain/56 |             0.00 |              0.000 |     0.000

```
