"""Meta loader that groups the per-token singleErc20 loaders.

It never fetches anything itself. Its name is the key under which every singleErc20
result is nested: account["chains"][chain]["ERC20 balances"][token loader name].
"""

from load0000rs.base import baseLoad0000r

NAME = "ERC20 balances"


class load0000r(baseLoad0000r):
    def name(self):
        return NAME

    def version(self):
        return "0.0.1"

    def analyze(self, account, chain):
        raise RuntimeError("the ERC20 meta loader only groups singleErc20 loaders; "
                           "pass those to loadAccountMetadata instead")
