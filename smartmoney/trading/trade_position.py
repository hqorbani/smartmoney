from dataclasses import dataclass
from enum import Enum

from smartmoney.trading.trade_plan import (
    TradeDirection,
    TradePlan,
)


class PositionStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"

class ExitReason(Enum):
    TAKE_PROFIT = "take_profit"
    STOP_LOSS = "stop_loss"
    MANUAL = "manual"

@dataclass(frozen=True, slots=True)
class TradePosition:
    """
    Represents an opened trade position.

    A TradePosition is the execution/lifecycle representation
    of a TradePlan.
    """

    plan: TradePlan
    size: float
    status: PositionStatus = PositionStatus.OPEN
    exit_price: float | None = None
    exit_reason: ExitReason | None = None
    @property
    def pnl(self) -> float | None:
        if self.status != PositionStatus.CLOSED:
            return None

        if self.exit_price is None:
            return None

        price_difference = (
            self.exit_price - self.plan.entry_price
        )

        if self.plan.direction == TradeDirection.SELL:
            price_difference = -price_difference

        return price_difference * self.size
    
    def close(
        self,
        exit_price: float,
        exit_reason: ExitReason,
    ) -> "TradePosition":
        if self.status == PositionStatus.CLOSED:
            raise ValueError(
                "Trade position is already closed"
            )

        if exit_price <= 0:
            raise ValueError(
                "Exit price must be positive"
            )

        if not exit_reason:
            raise ValueError(
                "Exit reason must not be empty"
            )

        if not isinstance(exit_reason, ExitReason):
            raise ValueError(
                "Invalid exit reason"
            )

        return TradePosition(
            plan=self.plan,
            size=self.size,
            status=PositionStatus.CLOSED,
            exit_price=exit_price,
            exit_reason=exit_reason,
        )