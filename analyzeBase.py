from abc import ABC, abstractmethod
from datetime import datetime

class analyzeBase(ABC):
    
    @abstractmethod
    def name (self):
        pass
    
    @abstractmethod
    def version(self):
        pass
    
    @abstractmethod
    def analyze(self, account):
        pass

    def createEmptyAccountEntry(self):
        return({
            "version": self.version(),
            "lastRun": datetime.utcnow().strftime("%Y-%m-%d--%H-%M-%S")
            })
