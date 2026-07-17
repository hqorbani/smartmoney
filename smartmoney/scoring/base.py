from abc import ABC
from abc import abstractmethod


class ScoreRule(ABC):

    @abstractmethod
    def score(self, signal, context) -> float:
        ...