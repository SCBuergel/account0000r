"""Base class for account loaders.

A loader fetches one piece of data (a balance, a nonce, ...) for one account on one
chain. account0000r.loadAccountMetadata runs every loader for every account on every
chain and stores each result at

    account["chains"][chain name][loader name]

or, for a child loader that belongs to a meta loader (one loader per ERC-20 token),

    account["chains"][chain name][meta loader name][loader name]
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone


def targetBlock(chain, atBlock):
    """The block to query: the chain's stored end-of-year block, or "latest"."""
    if not atBlock:
        return "latest"
    return chain["metadata"]["blockNumberByTimestamp"]["blockNumber"]


class baseLoad0000r(ABC):
    # True: skip accounts that already have a result for this loader (used for re-runs).
    _shouldSkipAnalysisIfEntryExists = False
    # Child loaders set this to their meta loader; results are then nested under its name.
    _metaLoad0000r = None

    @abstractmethod
    def name(self):
        """Key under which results are stored. Unique per loader instance."""

    @abstractmethod
    def version(self):
        """Version string stored with every result."""

    def appliesTo(self, chain):
        """Whether analyze() has anything to do on `chain`; loaders bound to one chain
        override this so that no task is scheduled for the others."""
        return True

    @abstractmethod
    def analyze(self, account, chain):
        """Fetch data for `account` (checksummed address string) on `chain` (a dict from
        chains.json). Return createEmptyAccountEntry() with the result added, or None to
        store nothing. Runs in a worker thread: do not touch shared state."""

    def createEmptyAccountEntry(self):
        return {
            "version": self.version(),
            "lastRun": datetime.now(timezone.utc).strftime("%Y-%m-%d--%H-%M-%S"),
        }

    def existingEntry(self, account, chain):
        """This loader's stored result for `account` on `chain`, or None."""
        container = account.get("chains", {}).get(chain["name"], {})
        if self._metaLoad0000r is not None:
            container = container.get(self._metaLoad0000r.name(), {})
        return container.get(self.name())

    def skipAnalysisIfEntryExists(self, account, chain):
        return self._shouldSkipAnalysisIfEntryExists and self.existingEntry(account, chain) is not None
