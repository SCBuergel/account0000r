import json
import account0000r
from load0000rs import ethBalance, nonce, airdropOpApi, airdropHopApi, airdropHopJson, erc20BalanceAtBlock, erc20Balance, metaLoad0000rErc20
import analyz0000r
import chainLoad0000rs



### 1. DERIVE ACCOUNTS FROM SECRETS, FIND VOID ACCOUNTS, STORE, DISPLAY
print("loading secrets and chains...")
#secrets = json.load(open("data/secrets.json"))
#accounts = account0000r.accountsFromSecrets(secrets)
#accounts0 = json.load(open("data/accounts-2022-07-06--21-50-57--hard.json"))
#accounts1 = json.load(open("data/accounts-2023-07-08--15-10-33.json"))
#accounts = [*accounts0, *accounts1]

#accounts = json.load(open("data/accounts-blank-sample.json"))
#chains = json.load(open("data/chains-eoy2022-tokens.json"))

#print("loading account metadata...")
#accounts = account0000r.loadAccountMetadata([nonce.load0000r()], accounts, chains)

#print("writing json...")
#account0000r.writeJson(accounts)

#print("printing results...")
#analyz0000r.listAccountsNonZero(accounts, load0000r="ETH balance at block", dust=0.01)
#analyz0000r.tabulateAllAccounts(accounts)
#analyz0000r.tabulateNonZeroNonce(accounts)
#analyz0000r.listAccountsNonZero(accounts)



### 2. OPEN ACCOUNTS, FIND EOY BLOCKS, LOAD EOY BALANCE, STORE, DISPLAY
atBlock = False
eoy2022 = 1672527600
accounts = json.load(open("data/accounts-blank.json"))
chains = json.load(open("data/chains.json"))
#chains = account0000r.getBlockNoFromTimestamp(chains, eoy2022)

# write JSON with EOY block numbers so that the above block number reading
# does not have to be run every time
#account0000r.writeJson(chains, fileName="data/chains-sample-eoy2022.json")


#metaErc20 = metaLoad0000rErc20.load0000r()
#erc20Load0000rs, chains = account0000r.generateTokenLoad0000rs(chains, metaErc20, loadChainData=True, atBlock=atBlock)

# write JSON with token decimals so that the above decimal reading
# does not have to be run every time
#account0000r.writeJson(chains, "data/chains-eoy2022-tokens.json")

#accounts, errors = account0000r.loadAccountMetadata([ethBalance.load0000r(atBlock=atBlock), *erc20Load0000rs], accounts, chains)
#accounts = account0000r.loadAccountMetadata([ethBalanceAtBlock.load0000r()], accounts, chains)
#account0000r.writeJson(accounts)

"""



#csvOutputFile = "data/new-accountingEnd2021.csv"
#accountBalances.to_csv(csvOutputFile)
#errors.to_csv("data/errors.csv")



TODO
3. handle load0000rs with remote API calls in queue
3.1. [DONE] Add flag property to base load0000r and if the flag is set, execution is delayed and the load0000r call is instead pushed into a shuffled queue
3.2. build queue of load0000r runs that should be run and append to shuffled queue

4. handle request/response errors that currently crash the script pushing the call back into the queue, shuffle queue and try again later

5. update CSV file with results after each load0000r result is available instead of running all of them and only then write, so that no data is lost in case the script crashes

6. add optional middleware ahead of load0000r to change IP of VPN (only run this for load0000rs which actually call RPCs)
"""
#accounts = account0000r.loadAccountMetadata(erc20Load0000rs, accounts, chains)
#account0000r.writeJson(accounts)


### 3. OPEN ACCOUNTS, DISPLAY
accounts = json.load(open("data/accounts-2023-12-31--20-01-37--LATEST.json"))
accountBalances = analyz0000r.portfolioValue(accounts, chains, assetPricesCsv="data/assetPrices-EOY2022.csv", atBlock=atBlock)

#df = analyz0000r.listAllNonDustBalances(accounts, chains, atBlock=True)

#csvOutputFile = "data/accountingEnd2021.csv"
#accountBalances.to_csv(csvOutputFile)
analyz0000r.tableAccountsNonZeroBalance(accounts, load0000r="ETH balance")
#analyz0000r.printAllAccountUse(accounts)
#analyz0000r.tabulateAllAccounts(accounts)
#analyz0000r.tabulateNonZeroNonce(accounts)
#analyz0000r.listAccountsNonZero(accounts)
