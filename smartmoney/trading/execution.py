from dataclasses import dataclass
from enum import Enum

from smartmoney.trading.trade_plan import (
    TradeDirection,
    TradePlan,
)

class ExecutionStatus(Enum):
    DRY_RUN = "dry_run"
    EXECUTED = "executed"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    status: ExecutionStatus
    plan: TradePlan
    message: str

from abc import ABC, abstractmethod
class TradeExecutor(ABC):
    """
    Interface for trade execution implementations.
    """

    @abstractmethod
    def execute(self, plan: TradePlan) -> ExecutionResult:
        """
        Execute or simulate a trade plan.
        """
        raise NotImplementedError
    
class DryRunExecutor(TradeExecutor):
    """
    Simulate trade execution without sending any order to a broker.
    """

    def execute(self, plan: TradePlan) -> ExecutionResult:
        if plan.risk_distance <= 0:
            return ExecutionResult(
                status=ExecutionStatus.REJECTED,
                plan=plan,
                message="Trade plan risk must be positive",
            )

        if plan.direction == TradeDirection.BUY:
            if not (
                plan.stop_loss < plan.entry_price < plan.take_profit
            ):
                return ExecutionResult(
                    status=ExecutionStatus.REJECTED,
                    plan=plan,
                    message="Invalid BUY trade levels",
                )

        elif plan.direction == TradeDirection.SELL:
            if not (
                plan.take_profit < plan.entry_price < plan.stop_loss
            ):
                return ExecutionResult(
                    status=ExecutionStatus.REJECTED,
                    plan=plan,
                    message="Invalid SELL trade levels",
                )

        return ExecutionResult(
            status=ExecutionStatus.DRY_RUN,
            plan=plan,
            message="Dry-run order accepted",
        )