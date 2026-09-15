from abc import ABC, abstractmethod

from smartmoney.trading.execution import ExecutionResult
from smartmoney.trading.trade_plan import TradePlan


class BrokerExecutor(ABC):
    """
    Interface for broker-specific trade execution.

    Concrete implementations, such as MT5 execution,
    will be added later.
    """

    @abstractmethod
    def execute(
        self,
        plan: TradePlan,
    ) -> ExecutionResult:
        raise NotImplementedError