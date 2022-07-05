# account0000r.

This tool lets you check EVM accounts accross chains. It keeps a local record in a JSON file and is aimed at being easily extendable.

account0000r is built for managing accounts in independent steps:
1. `accountsFromSecrets`: derive list of addresses from mnemonic & passphrase
2. `storeAccounts`: store list of addresses
3. load addresses
4. `analyzeAccounts`: analyze addresses on various chains (balances, nonces, airdrops), chains are specified in the `chains.json` file

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
