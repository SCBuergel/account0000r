import json
import account0000r
from load0000rs import ethBalance, ethBalanceAtBlock, nonce, airdropOpApi, airdropHopApi, airdropHopJson
from analyz0000r import listAccountsNonZero, listAccountsNonZeroAtBlock, tableAccountsNonZeroBalance, listAccountsAirdropOP, listAccountsAirdropHop



### 1. INITIAL ACCOUNT CREATION
# secrets = json.load(open("secrets.json"))
# accounts = account0000r.accountsFromSecrets(secrets)



### 2. LOAD BASIC METADATA OF ACCOUNTS AND STORE IN FILE
# accounts = account0000r.loadAccountMetadata([nonce.load0000r(), ethBalance.load0000r()], accounts)
# account0000r.storeAccounts(accounts)



### get end of year timestamps
# endOf2021Timestamp = 1640991600
# blockNumbersEnd2021 = account0000r.getBlockNumberByTime(endOf2021Timestamp, chains)
# print(f"cutoff block numbers: {blockNumbersEnd2021}")
# newFile = open("data/blockNumbersEnd2021.json", "w")
# newFile.write(json.dumps(blockNumbersEnd2021, indent=2))
# newFile.close()




### 3. RESTORE ACCOUNTS FROM FILE, LOAD MORE METADATA AND STORE AGAIN
# some sample analysis
chains = json.load(open("chains.json"))
# chains = chains[4:]
# dataFile = "data/accounts-2022-12-10--23-42-58.json"
dataFile = "data/accounts-2022-12-13--00-41-45.json"
accounts = json.load(open(dataFile))
# accounts = account0000r.loadAccountMetadata([ethBalanceAtBlock.load0000r()], accounts, chains)
#accounts = account0000r.loadAccountMetadata([airdropHopApi.load0000r()], accounts, chains)
#outputFile = account0000r.storeAccounts(accounts)
#print("stored output file ", outputFile)

### 4. PRINT ANALYSIS ON ACCOUNT DATA
listAccountsNonZero(accounts)
listAccountsNonZeroAtBlock(accounts)
"""
tableAccountsNonZeroBalance(accounts)
listAccountsAirdropHop(accounts)
listAccountsAirdropOP(accounts)
"""

