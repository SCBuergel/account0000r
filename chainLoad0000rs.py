from web3 import Web3
from load0000rs.base import baseLoad0000r
from web3.middleware import geth_poa_middleware

class blockNumberByTimestamp(baseLoad0000r):
    timestamp = 0

    def __init__(self, timestamp):
        self.timestamp = timestamp

    def name(self):
        return "blockNumberByTimestamp"

    def version(self):
        return "0.0.1"

    def analyze(self, chain, accounts):
        web3 = Web3(Web3.HTTPProvider(chain["api"]))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        smallerBlock = web3.eth.get_block(1, False)
        biggerBlock = web3.eth.get_block("latest", False)
        print(f"Looking for timestamp {self.timestamp} on {chain['name']}")
        if (self.timestamp < smallerBlock.timestamp):
            print(f"Error: targer timestamp {self.timestamp} is earlier than the timestamp of block number 1 on {chain['name']} which is {smallerBlock.timestamp}")
            return
        elif (self.timestamp > biggerBlock.timestamp):
            print(f"Error: target timestamp {self.timestamp} is later than the timestamp of the latest block (block number {biggerBlock.number}) on {chain['name']} which is {biggerBlock.timestamp}")
            return
        else:
            while (True):
                print(f"smaller block number: {smallerBlock.number}, timestamp: {smallerBlock.timestamp}")
                print(f"bigger block number:  {biggerBlock.number}, timestamp: {biggerBlock.timestamp}")
                nextBlockNo = int((biggerBlock.number + smallerBlock.number) / 2)
                nextBlock = web3.eth.get_block(nextBlockNo, False)
                if (nextBlock.timestamp >= self.timestamp):
                    if (nextBlock.number == biggerBlock.number):
                        print(f"we're close enough, quitting here")
                        break;
                    biggerBlock = nextBlock
                else:
                    if (nextBlock.number == smallerBlock.number):
                        print(f"we're close enough, quitting here")
                        break;
                    smallerBlock = nextBlock

        print(f"block {nextBlock.number} on {chain['name']} happened at time {nextBlock.timestamp}")
        return {
                  "timestamp": self.timestamp,
                  "blockNumber": nextBlock.number
                }

