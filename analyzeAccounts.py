import json
def analyzeAccounts(analyz0000rs, accounts, chainsFileName="chains.json"):
    chains = json.load(open("chains.json"))
    for ci in range(len(chains)):
        c = chains[ci]
        for a in range(len(accounts)):
            print(f"progress: {(ci * len(accounts) + a) / (len(chains) * len(accounts)) * 100:.2f}%")
            address = accounts[a]["address"]
            for analyz0000r in analyz0000rs:
                newEntry = analyz0000r.analyze(address, c)
                if (c["name"] not in accounts[a]["chains"]):
                    accounts[a]["chains"][c["name"]] = {}

                accounts[a]["chains"][c["name"]][analyz0000r.name()] = newEntry
    return accounts


