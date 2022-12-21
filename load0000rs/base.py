from abc import ABC, abstractmethod
from datetime import datetime

class baseLoad0000r(ABC):
    """Abstract base class from which other load0000r modules that implement analysis functionality are derived
    """
    
    @abstractmethod
    def name(self):
        """The implementation function returns the name of the load0000r module

        Returns
        -------
        string
            Name of the derived load0000r module
        """
        pass
    
    @abstractmethod
    def version(self):
        """The implementation functions returns the semver-styled version of the load0000r module

        Returns
        -------
        string
            Semver version number of the derived load0000r module
        """
        pass
    
    @abstractmethod
    def analyze(self, account):
        """The implementation function that runs the actual analysis of the account and writes a new result entry into the account object

        Parameters
        ----------
        account : account
            account loaded by account0000r

        Returns
        -------
        account
            accounts with additional result entry from this analysis
        """
        pass

    def createEmptyAccountEntry(self):
        """Creates an empty result entry that is added to an account for each load0000r that is run

        Returns
        -------
        object
            An empty account entry with ["version"] and ["lastRun"] properties
        """
        return({
            "version": self.version(),
            "lastRun": datetime.utcnow().strftime("%Y-%m-%d--%H-%M-%S")
            })
