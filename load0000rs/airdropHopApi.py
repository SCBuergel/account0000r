# the API seems to be rate limited so this load0000r is unlikely going to work for >10 accounts
import requests
from load0000rs.base import baseLoad0000r

class load0000r(baseLoad0000r):
    def name(self):
        return "airdropHopApi"

    def version(self):
        return "0.0.1"

    def analyze(self, account, chain):
        if chain["name"] != "Ethereum Main Net":
            return {}
        url = "https://airdrop-api.hop.exchange/v1/airdrop/"
        # returns a response that looks as follows:
        #   {'status': 'ok', 'data': {'address': '0xd8da6bf26964af9d7eed9e03e53415d37aa96045', 'totalTxs': '2', 'totalVolume': '5571.29898895669', 'lpTokens': '0', 'hopUserTokens': '1354449569615422850987', 'earlyMultiplier': '1.3661093739913863', 'volumeMultiplier': '3', 'totalTokens': '1354449569615422850987', 'bridgeUserBaseAmount': '330488318481192350341
        # or response for no airdrop
        # {"status":"ok","data":{"totalTokens":"0"}}

        response = requests.get(url + account)
        respJson = response.json()
        newEntry = self.createEmptyAccountEntry()
        newEntry["airdropHop"] = int(respJson["data"]["totalTokens"])/1e18
        if (newEntry["airdropHop"] > 0):
            print("Hop Airdrop: ", newEntry["airdropHop"], " for ", account)
        else:
            print("No Hop airdrop for:", account)
        return newEntry


