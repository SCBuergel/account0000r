import json
import account0000r
from load0000rs import ethBalance, ethBalanceAtBlock, nonce, airdropOpApi, airdropHopApi, airdropHopJson, erc20BalanceAtBlock, erc20Balance
import analyz0000r
import chainLoad0000rs



"""
### 1. DERIVE ACCOUNTS FROM SECRETS, FIND VOID ACCOUNTS, STORE, DISPLAY
secrets = json.load(open("data/secrets.json"))
accounts = account0000r.accountsFromSecrets(secrets)
chains = json.load(open("data/chains.json"))
accounts = account0000r.loadAccountMetadata([nonce.load0000r(), ethBalance.load0000r()], accounts, chains)
account0000r.writeJson(accounts)
analyz0000r.tabulateAllAccounts(accounts)
analyz0000r.tabulateNonZeroNonce(accounts)
analyz0000r.listAccountsNonZero(accounts)
"""



### 2. OPEN ACCOUNTS, FIND EOY BLOCKS, LOAD EOY BALANCE, STORE, DISPLAY
dataFile = "data/accounts-2022-12-29--15-30-38.json"
accounts = json.load(open(dataFile))
chains = json.load(open("data/chains-EOY2021.json"))
#accounts = account0000r.loadAccountMetadata([ethBalance.load0000r(), erc20Balance.load0000r(False)], accounts, chains)
#account0000r.writeJson(accounts)
accountBalances = analyz0000r.portfolioValue(accounts, chains, atBlock=False)
#csvOutputFile = "data/hard-accountingEnd2021.csv"
#accountBalances.to_csv(csvOutputFile)



"""
### 3. OPEN ACCOUNTS, DISPLAY
dataFile = "data/accounts-2022-12-28--18-18-28--EOY2021.json"
accounts = json.load(open(dataFile))
df = analyz0000r.listAllNonDustBalances(accounts)
csvOutputFile = "data/accountingEnd2021.csv"
df.to_csv(csvOutputFile)
"""

