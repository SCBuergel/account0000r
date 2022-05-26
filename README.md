# activETHchckr
Checking accounts for activity across chains

The tool is built for managing accounts in independent steps:
1. create accounts from mnemonic & passphrase
2. store accounts
3. load account
4. analyze accounts (balances, nonces, airdrops)

Requires an `secrets.json` file in the root directory which contains a list of mnemonics and passphrases, as follows:
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
