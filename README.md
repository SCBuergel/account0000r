# activETHchckr
Checking accounts for activity across chains

The tool is built for managing accounts in independent steps:
1. derive list of addresses from mnemonic & passphrase
2. store list of addresses
3. load addresses
4. analyze addresses on various chains (balances, nonces, airdrops), chains are specified in the `chains.json` file

Requires a `secrets.json` file in the root directory which contains a list of mnemonics and passphrases, as follows:
```
[
  {
    "mnemonic": "zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo wrong",
    "passphrase": ""
  },
  {
    "mnemonic": "zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo wrong",
    "passphrase": "rekt"
  }
]
```
