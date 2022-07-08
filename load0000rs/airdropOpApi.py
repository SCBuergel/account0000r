import requests
from load0000rs.base import baseLoad0000r

class load0000r(baseLoad0000r):
    def name(self):
        return "airdropOpApi"

    def version(self):
        return "0.0.1"

    def analyze(self, account, chain):
        if chain["name"] != "Optimism":
            return;
        url = "https://mainnet-indexer.optimism.io/v1/airdrops/"
        # returns a response that looks as follows:
        # {"address":"0x00000000000cd56832ce5dfbcbff02e7ec639bc9","voterAmount":"271833778900496351232","multisigSignerAmount":"0","gitcoinAmount":"0","activeBridgedAmount":"409426292836590288896","opUserAmount":"0","opRepeatUserAmount":"0","bonusAmount":"0","totalAmount":"681260071737086705664"}
        # or error response:
        # {'error': 'airdrop not found'}

        response = requests.get(url + account)
        respJson = response.json()
        print(respJson)
        newEntry = self.createEmptyAccountEntry()
        if "error" in respJson.keys():
            newEntry["airdropOp"] = 0
        else:
            newEntry["airdropOp"] = int(respJson["totalAmount"])/1e18
        return newEntry


