from dataclasses import dataclass
from enum import Enum

from smartmoney.trading.trade_plan import TradePlan


class PositionStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"


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
    exit_reason: str | None = None

    def close(
        self,
        exit_price: float,
        exit_reason: str,
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

        return TradePosition(
            plan=self.plan,
            size=self.size,
            status=PositionStatus.CLOSED,
            exit_price=exit_price,
            exit_reason=exit_reason,
        )