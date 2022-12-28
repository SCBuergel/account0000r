import json
import account0000r
from load0000rs import ethBalance, ethBalanceAtBlock, nonce, airdropOpApi, airdropHopApi, airdropHopJson, erc20BalanceAtBlock
from analyz0000r import listAccountsNonZero, tableAccountsNonZeroBalance, listAccountsAirdropOP, listAccountsAirdropHop, listAllNonDustBalances, tabulateNonZeroNonce
import chainLoad0000rs



### 1. INITIAL ACCOUNT CREATION
# secrets = json.load(open("secrets.json"))
# accounts = account0000r.accountsFromSecrets(secrets)



### 2. LOAD BASIC METADATA OF ACCOUNTS AND STORE IN FILE
# accounts = account0000r.loadAccountMetadata([nonce.load0000r(), ethBalance.load0000r()], accounts)
# account0000r.storeAccounts(accounts)




### 3. RESTORE ACCOUNTS FROM FILE, LOAD MORE METADATA AND STORE AGAIN
# some sample analysis
#chains = json.load(open("chainsSmall-Enriched.json"))
# chains = chains[4:]
dataFile = "data/accounts-2022-12-13--00-41-45.json"
#dataFile = "data/accountsBlank.json"
accounts = json.load(open(dataFile))
#ldr = erc20BalanceAtBlock.load0000r()#ldr.analyze(accounts[13], chains[0])

### LOAD CHAIN METADATA AND STORE AGAIN
# endOf2021Timestamp = 1640991600
# chainsEnriched = account0000r.loadChainMetadata([chainLoad0000rs.blockNumberByTimestamp(endOf2021Timestamp)], accounts, chains)
# account0000r.writeJson(chainsEnriched, "chainsSmall-Enriched.json")


#accounts = account0000r.loadAccountMetadata([ethBalanceAtBlock.load0000r(), erc20BalanceAtBlock.load0000r()], accounts, chains)
#accounts = account0000r.loadAccountMetadata([airdropHopApi.load0000r()], accounts, chains)
#outputFile = account0000r.writeJson(accounts)
#print("stored output file ", outputFile)



### 4. PRINT ANALYSIS ON ACCOUNT DATA
# listAccountsNonZero(accounts)

#listAccountsNonZero(accounts, "ETH balance at block")
#listAllNonDustBalances(accounts)
"""
tableAccountsNonZeroBalance(accounts)
listAccountsAirdropHop(accounts)
listAccountsAirdropOP(accounts)
"""
tabulateNonZeroNonce(accounts)
