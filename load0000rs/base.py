from abc import ABC, abstractmethod
from datetime import datetime

class baseLoad0000r(ABC):
    """Abstract base class from which other load0000r modules that implement analysis functionality are derived
    """
    
    def __new__(cls, *args, **kwargs):
        r = object.__new__(cls)

        # set this property to true (e.g. in constructor of derived class) to avoid running the analysis again if an entry for the load0000r already exists
        r._shouldSkipAnalysisIfEntryExists = False
        
        # if the derived class is a childLoad0000r, reference its metaLoad0000r here (eg. in constructor)
        r._metaLoad0000r = {}

        # load0000rs that identify as this can be handled via VPN, HOPR or other privacy-preserving means to call remote APIs in a privacy-preserving fashion
        r._callsRemoteApi = False

        return r

    @abstractmethod
    def name(self):
        """The implementation function returns the name of the load0000r module

        Returns
        
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

    def skipAnalysisIfEntryExists(self, account, chain):
        """Returns True if self._skipAnalysisIfEntryExists has been set and an entry in the account exists for the current load0000r
        
        Parameters
        ----------
        account
            object with account data

        Returns
        -------
        bool
            True if the analysis should be skipped
        """
        return (self._shouldSkipAnalysisIfEntryExists and 
                (self.name() in account["chains"][chain["name"]].keys() 
                    or (self._metaLoad0000r != {} 
                        and self._metaLoad0000r.name() in account["chains"][chain["name"]]
                        and self.name() in account["chains"][chain["name"]][self._metaLoad0000r.name()].keys())))
