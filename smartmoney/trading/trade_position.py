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

    def close(self) -> "TradePosition":
        if self.status == PositionStatus.CLOSED:
            raise ValueError(
                "Trade position is already closed"
            )

        return TradePosition(
            plan=self.plan,
            size=self.size,
            status=PositionStatus.CLOSED,
        )