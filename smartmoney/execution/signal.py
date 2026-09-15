from dataclasses import dataclass
from enum import Enum

from smartmoney.backtesting.orderblock_zones import (
    OrderBlockDepthZone,
)
from smartmoney.models.orderblock import OrderBlock


class TradeDirection(str, Enum):
    BUY = "buy"
    SELL = "sell"


@dataclass(frozen=True, slots=True)
class TradeSignal:
    symbol: str
    timeframe: int

    direction: TradeDirection

    orderblock: OrderBlock
    touch_zone: OrderBlockDepthZone

    entry_price: float
    stop_loss: float
    take_profit: float

    risk: float
    reward: float
    rr: float