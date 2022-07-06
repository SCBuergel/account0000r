# account0000r - extendable EVM account overview

account0000r lets you check EVM accounts accross chains. It keeps a local record in a JSON file and is aimed at being easily extendable. It helps you answer questions such as:

> On which chain did I use this account?

> Which of my 100 accounts has a balance > 0 on any chain?

> I backed up my mnemonic, but where are the accounts and which of them did I ever use?

> Do I have any unclaimed [ENTER PROJECT NAME] airdrops for any of my 100 accounts?

## Usage

account0000r comprises a set of Python tools to create accounts, load metadata of accounts and analyze them. 
See the `runn0000r.py` script for some usage examples.

The account0000r Python package is built for managing accounts in separate steps:

### `account0000r.accountsFromSecrets`
Returns a list of accounts with metadata from a mnemonic & passphrase setting file

### `account0000r.storeAccounts`
Stores the list of accounts and metadata. This file can be read at a later time for loading additional analysis into the metadata of each account.

### Load accounts
Since account metadata files stored as JSON, they can be loaded via
```
import json
accounts = json.load(open("accounts.json")) 
```

### `account0000r.analyzeAccounts`
Loads various account metadata from on various EVM chains. 
Simple examples that are included already now are balances, nonces of accounts but account0000r's extendable nature makes this step easily adjustable to load token balances, pending airdrop claims or other highly custom properties.
The chains from which metadata is loaded are specified in the `chains.json` file (see more info on settings files below).
The specific data is loaded via `load0000r` classes (locaded in the folder with the same name) that are all derived from an abstract `baseLoad0000r` class.
Instances of each `load0000r` are then passed as a list to the `account0000r.analyzeAccounts` function.
So in order to write your own `load0000r`, you can follow the examples in the `load0000rs` folder, `import` it in the `runn0000r.py` file and pass an instance of it to the list argument of the `account0000r.analyzeAccounts` function. 

## File and folder structure
```
.
├── data - contains JSON output files with account metadata
├── load0000rs
│   ├── base.py       - contains the base class `baseLoad0000r`
│   ├── ethBalance.py - native balance loader
│   └── nonce.py      - account nonce loader
├── EXAMPLE-secrets.json - rename this to `secrets.json` but make sure to never submit this file anywhere and only store on machines that you fully trust!
├── chains.json - the settings file of the chains from which to load metadata
├── account0000r.py - the main account0000r module with the main functions
├── runn0000r.py - an example file with snippets to initialize accounts, load metadata and run simple analysis on the acccounts metadata object
└── README.md - this README file
```



## Settings files
Requires a `secrets.json` file in the root directory which contains a list of mnemonics and passphrases, as follows:
```
[
  {
    "mnemonic": "zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo wrong",
    "description": "plain testvector mnemonic"
  },
  {
    "mnemonic": "zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo wrong",
    "passphrase": "rekt",
    "hdPath": "m/44'/60'/0'",
    "numAccounts": 20,
    "accountOffset": 1000,
    "description": "testvector mnemonic with password"
  }
]
```
The following are optional fields with indicated default values:
```
"passphrase" (default: "")
"hdPath" (default: "m/44'/60'/0'/0")
"numAccounts" (default: 10)
"accountOffset" (default: 0)
"description" (default: "")
```

It also requires a `chains.json` file in the root directory with a list of chain names and RPC endpoints:
```
[
  {
    "name": "Ethereum Main Net",
    "api": "https://rpc.ankr.com/eth"
  },
  {
    "name": "Gnosis Chain",
    "api": "https://rpc.ankr.com/gnosis"
  }
]
```

