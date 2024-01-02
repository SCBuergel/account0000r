# the API seems to be rate limited so this load0000r is unlikely going to work for >10 accounts
import requests
from load0000rs.base import baseLoad0000r

class load0000r(baseLoad0000r):
    def name(self):
        return "airdropDymApi"

    def version(self):
        return "0.0.1"

    def analyze(self, account, chain):
        if chain["name"] != "Ethereum Main Net":
            return {}
        url = "https://geteligibleuserrequest-xqbg2swtrq-uc.a.run.app/?address="
        # returns a response that looks as follows:
        # {"claimAddress":"0x35f0686c63f50707ea3b5bace186938e4e19f03a","amount":12946.526572053659}
        # or error 404
        #   {'status': 'ok', 'data': {'address': '0xd8da6bf26964af9d7eed9e03e53415d37aa96045', 'totalTxs': '2', 'totalVolume': '5571.29898895669', 'lpTokens': '0', 'hopUserTokens': '1354449569615422850987', 'earlyMultiplier': '1.3661093739913863', 'volumeMultiplier': '3', 'totalTokens': '1354449569615422850987', 'bridgeUserBaseAmount': '330488318481192350341
        # or response for no airdrop
        # {"status":"ok","data":{"totalTokens":"0"}}

        response = requests.get(url + account)
        newEntry = self.createEmptyAccountEntry()
        try:
            respJson = response.json()
            entry = float(respJson["amount"])
        except Exception as e:
            entry = 0
        
        newEntry["airdropDym"] = entry
        if (entry > 0):
            print("Dym Airdrop: ", entry, " for ", account)
        else:
            print("No Dym airdrop for:", account)
        return newEntry


