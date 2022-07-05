import json
import sys
from datetime import datetime
from accountsFromSecrets import accountsFromSecrets
from analyzeAccounts import analyzeAccounts
from analyzeNonce import analyzeNonce
from analyzeEthBalance import analyzeEthBalance


# this will create or overwrite the file
def storeAccounts(accounts, accountFileName="accounts-" + datetime.now().strftime("%Y-%m-%d--%H-%M-%S") + ".json"):
    file = open(accountFileName, "w")
    prettyAccounts = json.dumps(accounts, indent=2)
    file.write(prettyAccounts)
    file.close()

secrets = json.load(open("secrets.json"))
accounts = accountsFromSecrets(secrets)
accounts = analyzeAccounts([analyzeNonce(), analyzeEthBalance()], accounts)
storeAccounts(accounts)

# some sample analysis - printing all accounts and chain names with non-zero balance
dataFile = "accounts-2022-07-04--22-30-36.json"
accounts = json.load(open(dataFile))
for a in accounts:
    for c in a["chains"].items():
        if c[1]["ETH balance"]["nativeBalance"] > 0:
            print(f'{a["address"]} on {c[0]}')



