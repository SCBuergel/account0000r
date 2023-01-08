import json
import account0000r
from load0000rs import ethBalance, ethBalanceAtBlock, nonce, airdropOpApi, airdropHopApi, airdropHopJson, erc20BalanceAtBlock, erc20Balance, metaLoad0000rErc20
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
chains = json.load(open("data/chains-EOY2021-decimals-short.json"))
#accounts = account0000r.loadAccountMetadata([ethBalance.load0000r(), erc20Balance.load0000r(False)], accounts, chains)
#account0000r.writeJson(accounts)
#accountBalances = analyz0000r.portfolioValue(accounts, chains, atBlock=False)
#csvOutputFile = "data/hard-accountingEnd2021.csv"
#accountBalances.to_csv(csvOutputFile)

"""
TODO
1. [DONE] Introduce metaload0000rs - they comprise several child load0000rs within a single metaload0000r. E.g. an "erc20 balance load0000r" is a metada load0000r that contains several load0000rs, one per token. Other examples could be Uniswap LP load0000r, Compound, Aave, Yearn deposit load0000r
1.1 [DONE] add isMetaload0000r to baseLoad0000r (default `False`, should be set in constructor)
1.2 [DONE] add metaLoad0000r field to baseLoad0000r (default is empty), in case of a child load0000r, this field gets set to an instance of its corresponding metaLoad0000r
1.3 [DONE] the child load0000r's analyze() function needs to append its result to the metaload0000r and not directly to the chain object under an account object

2. break down ERC20 load0000r into separate instances, one per (chain + address)
2.1. [DONE] Write new SingleErc20Load0000r handling only one token on one chain
2.2. [DONE] preprocessing step, similar to finding block number of timestamps: load token metadata such as decimals of all tokens on all chains (in randomized order)
2.3. [DONE] preprocessing step: generate ERC20 load0000rs from chains.json within runn0000r.py

3. handle load0000rs with remote API calls in queue
3.1. [DONE] Add flag property to base load0000r and if the flag is set, execution is delayed and the load0000r call is instead pushed into a shuffled queue
3.2. build queue of load0000r runs that should be run and append to shuffled queue

4. handle request/response errors that currently crash the script pushing the call back into the queue, shuffle queue and try again later

5. update CSV file with results after each load0000r result is available instead of running all of them and only then write, so that no data is lost in case the script crashes

6. add optional middleware ahead of load0000r to change IP of VPN (only run this for load0000rs which actually call RPCs)
"""
metaErc20 = metaLoad0000rErc20.load0000r()
erc20Load0000rs, chains = account0000r.generateTokenLoad0000rs(chains, metaErc20)
account0000r.writeJson(chains, "data/chains-EOY2021-decimals.json")
accounts = account0000r.loadAccountMetadata(erc20Load0000rs, accounts, chains)
account0000r.writeJson(accounts)


"""
### 3. OPEN ACCOUNTS, DISPLAY
dataFile = "data/accounts-2022-12-28--18-18-28--EOY2021.json"
accounts = json.load(open(dataFile))
df = analyz0000r.listAllNonDustBalances(accounts)
csvOutputFile = "data/accountingEnd2021.csv"
df.to_csv(csvOutputFile)
"""

