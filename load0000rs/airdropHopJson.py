# this load0000r needs the following repository to be checked out in a parallel folder to the base folder of this repo: https://github.com/SCBuergel/airdropData
import json
from load0000rs.base import baseLoad0000r

class load0000r(baseLoad0000r):
    def __init__(self):
        csvFileName = "../airdropData/HopAirdrop.json"
        self.csvData = json.load(open(csvFileName))
        print(self.csvData[0]["owner"])

    def name(self):
        return "airdropHopJson"

    def version(self):
        return "0.0.1"

    def analyze(self, account, chain):
        if chain["name"] != "Ethereum Main Net":
            return {}
        airdrops = [int(x["balance"])/1e18 for x in self.csvData if x["owner"] == account.lower()]
        if len(airdrops) > 1:
            print("Warning, expected at most 1 airdrop for account ", account, " but found ", len(aidrops))
        airdropAmount = sum(airdrops)
        newEntry = self.createEmptyAccountEntry()
        newEntry["amountToken"] = airdropAmount
        return newEntry

