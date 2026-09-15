from smartmoney.trading.trade_position import TradePosition
from smartmoney.models.position_size import PositionSizePlan
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
    position_size_plan: PositionSizePlan | None = None
    broker_result: object | None = None

    def to_position(self) -> TradePosition:
        if self.status != ExecutionStatus.DRY_RUN:
            raise ValueError(
                "Only successful execution results can create a position"
            )

        if self.position_size_plan is None:
            raise ValueError(
                "Position size plan is required to create a position"
            )

        return TradePosition(
            plan=self.plan,
            size=self.position_size_plan.position_size,
        )
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
    def __init__(
        self,
        position_size_plan: PositionSizePlan | None = None,
        open_trades: list[TradePlan] | None = None,
        max_open_trades_per_symbol: int | None = None,
    ) -> None:
        self.position_size_plan = position_size_plan
        self.open_trades = open_trades or []
        self.max_open_trades_per_symbol = max_open_trades_per_symbol
        if (
            self.max_open_trades_per_symbol is not None
            and self.max_open_trades_per_symbol <= 0
        ):
            raise ValueError(
                "max_open_trades_per_symbol must be positive"
            )

    def execute(self, plan: TradePlan) -> ExecutionResult:
        if not plan.symbol:
            return ExecutionResult(
                status=ExecutionStatus.REJECTED,
                plan=plan,
                message="Symbol must not be empty",
                position_size_plan=self.position_size_plan,
            )
        if plan.timeframe <= 0:
            return ExecutionResult(
                status=ExecutionStatus.REJECTED,
                plan=plan,
                message="Timeframe must be positive",
                position_size_plan=self.position_size_plan,
            )
        if not isinstance(plan.direction, TradeDirection):
            return ExecutionResult(
                status=ExecutionStatus.REJECTED,
                plan=plan,
                message="Invalid trade direction",
                position_size_plan=self.position_size_plan,
            )
        if plan.risk_distance <= 0:
            return ExecutionResult(
                status=ExecutionStatus.REJECTED,
                plan=plan,
                message="Trade plan risk must be positive",
            )
        for open_trade in self.open_trades:
            if (
                open_trade.symbol == plan.symbol
                and open_trade.timeframe == plan.timeframe
                and open_trade.direction == plan.direction
            ):
                return ExecutionResult(
                    status=ExecutionStatus.REJECTED,
                    plan=plan,
                    message="Duplicate trade",
                    position_size_plan=self.position_size_plan,
                )
        if self.max_open_trades_per_symbol is not None:
            symbol_open_trades = sum(
                1
                for open_trade in self.open_trades
                if open_trade.symbol == plan.symbol
            )

            if symbol_open_trades >= self.max_open_trades_per_symbol:
                return ExecutionResult(
                    status=ExecutionStatus.REJECTED,
                    plan=plan,
                    message="Maximum open trades reached for symbol",
                    position_size_plan=self.position_size_plan,
                )
        if (
            self.position_size_plan is not None
            and self.position_size_plan.position_size <= 0
        ):
            return ExecutionResult(
                status=ExecutionStatus.REJECTED,
                plan=plan,
                message="Position size must be positive",
                position_size_plan=self.position_size_plan,
            )
        if (
            self.position_size_plan is not None
            and self.position_size_plan.risk_amount <= 0
        ):
            return ExecutionResult(
                status=ExecutionStatus.REJECTED,
                plan=plan,
                message="Risk amount must be positive",
                position_size_plan=self.position_size_plan,
            )
        if (
            self.position_size_plan is not None
            and self.position_size_plan.stop_distance <= 0
        ):
            return ExecutionResult(
                status=ExecutionStatus.REJECTED,
                plan=plan,
                message="Stop distance must be positive",
                position_size_plan=self.position_size_plan,
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
            position_size_plan=self.position_size_plan,
        )
    