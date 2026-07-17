from abc import ABC
from abc import abstractmethod

from smartmoney.core.context import MarketContext
from smartmoney.models.signal import Signal


class Scanner(ABC):

    @abstractmethod
    def scan(
        self,
        context: MarketContext,
    ) -> list[Signal]:

        ...