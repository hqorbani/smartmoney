from abc import ABC
from abc import abstractmethod


class Analyzer(ABC):

    priority = 100

    @abstractmethod
    def analyze(self, context):

        ...