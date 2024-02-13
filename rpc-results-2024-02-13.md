RPC performance measurements done via `python rpc-test.py` from Germany on 2024-02-13:

## mainnet
```
                                                                                            RPC provider | success rate [%] | median latency [s] | stdev [s]
                                                                           https://rpc.notadegen.com/eth |           100.00 |              0.103 |     0.020
                                                                               https://rpc.mevblocker.io |           100.00 |              0.137 |     0.007
                                                                              https://rpc.builder0x69.io |           100.00 |              0.140 |     0.017
                                                                     https://rpc.mevblocker.io/noreverts |           100.00 |              0.141 |     0.010
                                                                          https://rpc.mevblocker.io/fast |           100.00 |              0.141 |     0.063
                                                                             https://eth-pokt.nodies.app |           100.00 |              0.144 |     0.013
                                                                   https://rpc.mevblocker.io/fullprivacy |           100.00 |              0.149 |     0.005
                                                                                https://rpc.ankr.com/eth |           100.00 |              0.160 |     0.113
                                                                                    https://eth.drpc.org |           100.00 |              0.302 |     0.137
                                                                               https://rpc.flashbots.net |           100.00 |              0.409 |     0.056
                                                                                https://eth.llamarpc.com |           100.00 |              0.409 |     0.030
                                                                             https://eth.nodeconnect.org |           100.00 |              0.410 |     0.053
                                                                          https://rpc.flashbots.net/fast |           100.00 |              0.441 |     0.518
                                                                         https://rpc.tornadoeth.cash/eth |           100.00 |              0.462 |     0.234
                                                                                   https://eth.merkle.io |           100.00 |              0.472 |     0.071
                                                                              https://cloudflare-eth.com |           100.00 |              0.511 |     0.127
                                                                             https://core.gashawk.io/rpc |           100.00 |              0.621 |     0.063
                                                                                     https://1rpc.io/eth |           100.00 |              1.230 |     0.146
                                                    https://endpoints.omniatech.io/v1/eth/mainnet/public |            80.00 |              2.667 |     1.713
                                                              https://gateway.tenderly.co/public/mainnet |            70.00 |              0.110 |     0.038
                                                                     https://mainnet.gateway.tenderly.co |            60.00 |              0.105 |     0.028
                                                          https://ethereum.blockpi.network/v1/rpc/public |            60.00 |              0.117 |     0.006
                                                                  https://eth-mainnet.public.blastapi.io |            40.00 |              0.219 |     0.098
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
                                         https://rpc.ankr.com/gnosis |           100.00 |              0.155 |     0.081
                                  https://rpc.tornadoeth.cash/gnosis |           100.00 |              0.613 |     0.187
                        https://gnosis.blockpi.network/v1/rpc/public |            90.00 |              0.133 |     0.014
             https://endpoints.omniatech.io/v1/gnosis/mainnet/public |            90.00 |              2.252 |     1.631
                           https://gnosis-mainnet.public.blastapi.io |            80.00 |              0.495 |     0.060
                                             https://gnosis.drpc.org |            50.00 |              0.484 |     0.093
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
                        https://mainnet.optimism.io |           100.00 |              0.135 |     0.011
                      https://rpc.ankr.com/optimism |           100.00 |              0.149 |     0.029
                          https://optimism.drpc.org |           100.00 |              0.410 |     0.661
               https://rpc.tornadoeth.cash/optimism |           100.00 |              0.512 |     0.214
                                 https://1rpc.io/op |           100.00 |              1.132 |     0.253
https://endpoints.omniatech.io/v1/op/mainnet/public |            90.00 |              2.355 |     1.150
        https://gateway.tenderly.co/public/optimism |            70.00 |              0.114 |     0.011
     https://optimism.blockpi.network/v1/rpc/public |            70.00 |              0.120 |     0.018
               https://optimism.gateway.tenderly.co |            60.00 |              0.108 |     0.014
        https://optimism-mainnet.public.blastapi.io |            40.00 |              0.452 |     0.019
          https://optimism.api.onfinality.io/public |            30.00 |              0.713 |     0.154
                    https://rpc.optimism.gateway.fm |            10.00 |              0.471 |     0.000
     https://api.zan.top/node/v1/opt/mainnet/public |             0.00 |              0.000 |     0.000
                         https://op-pokt.nodies.app |             0.00 |              0.000 |     0.000
                      https://optimism.llamarpc.com |             0.00 |              0.000 |     0.000
                       https://optimism.meowrpc.com |             0.00 |              0.000 |     0.000
                    https://optimism.publicnode.com |             0.00 |              0.000 |     0.000
```

## arbitrum
```
                                         RPC provider | success rate [%] | median latency [s] | stdev [s]
                        https://rpc.ankr.com/arbitrum |           100.00 |              0.136 |     0.055
                 https://rpc.arb1.arbitrum.gateway.fm |           100.00 |              0.404 |     0.318
                 https://rpc.tornadoeth.cash/arbitrum |           100.00 |              0.422 |     4.055
       https://arbitrum.blockpi.network/v1/rpc/public |            90.00 |              0.134 |     0.044
https://endpoints.omniatech.io/v1/arbitrum/one/public |            90.00 |              2.355 |     2.699
                 https://arb-mainnet-public.unifra.io |            80.00 |              0.361 |     0.134
              https://arbitrum-one.public.blastapi.io |            10.00 |              2.456 |     0.000
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
                                                                                     https://polygon-rpc.com |           100.00 |              0.137 |     0.099
                                                                         https://rpc.tornadoeth.cash/polygon |           100.00 |              0.445 |     0.139
                                                                                       https://1rpc.io/matic |           100.00 |              1.176 |     0.135
                                                                  https://gateway.tenderly.co/public/polygon |            90.00 |              0.113 |     0.085
                                                                                    https://polygon.drpc.org |            90.00 |              0.511 |     0.172
                                                      https://endpoints.omniatech.io/v1/matic/mainnet/public |            90.00 |              3.181 |     2.710
                                                                         https://polygon.gateway.tenderly.co |            70.00 |              0.113 |     0.019
                                                                    https://polygon.api.onfinality.io/public |            40.00 |              0.613 |     0.045
                                                               https://polygon.blockpi.network/v1/rpc/public |            30.00 |              0.134 |     0.007
                                                                                https://polygon.llamarpc.com |            30.00 |              0.924 |     0.108
                                                                  https://polygon-mainnet.public.blastapi.io |            10.00 |              0.211 |     0.000
                                                                          https://polygon-bor.publicnode.com |             0.00 |              0.000 |     0.000
https://polygon-mainnet.rpcfast.com?api_key=xbhWBI1Wkguk8SNMu1bvvLurPGLXmgwYeC4S6g2H7WdwFigZSmPWVZRxrskEQwIf |             0.00 |              0.000 |     0.000
                                                                             https://polygon-pokt.nodies.app |             0.00 |              0.000 |     0.000
                                                                                 https://polygon.meowrpc.com |             0.00 |              0.000 |     0.000
                                                                             https://polygon.rpc.blxrbdn.com |             0.00 |              0.000 |     0.000
                                                                      https://rpc-mainnet.matic.quiknode.pro |             0.00 |              0.000 |     0.000
                                                                          https://rpc-mainnet.maticvigil.com |             0.00 |              0.000 |     0.000
                                                                                https://rpc.ankr.com/polygon |             0.00 |              0.000 |     0.000
```
