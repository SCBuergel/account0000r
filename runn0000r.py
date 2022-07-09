import json
import account0000r
from load0000rs import ethBalance, nonce, airdropOpApi
from analyz0000r import listAccountsNonZero, tableAccountsNonZeroBalance, listAccountsAirdropOP



### 1. INITIAL ACCOUNT CREATION
# secrets = json.load(open("secrets.json"))
# accounts = account0000r.accountsFromSecrets(secrets)



### 2. LOAD BASIC METADATA OF ACCOUNTS AND STORE IN FILE
# accounts = account0000r.loadAccountMetadata([nonce.load0000r(), ethBalance.load0000r()], accounts)
# account0000r.storeAccounts(accounts)



### 3. RESTORE ACCOUNTS FROM FILE, LOAD MORE METADATA AND STORE AGAIN
# some sample analysis
dataFile = "data/accountsBlank.json"
accounts = json.load(open(dataFile))
accounts = account0000r.loadAccountMetadata([nonce.load0000r(), ethBalance.load0000r(), airdropOpApi.load0000r()], accounts)
account0000r.storeAccounts(accounts)



### 4. PRINT ANALYSIS ON ACCOUNT DATA
listAccountsNonZero(accounts)
tableAccountsNonZeroBalance(accounts)
listAccountsAirdropOP(accounts)
