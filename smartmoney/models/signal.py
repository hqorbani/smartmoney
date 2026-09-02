from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from smartmoney.models.fvg import FVG
from smartmoney.models.orderblock import OrderBlock


class SignalDirection(str, Enum):
    BUY = "buy"
    SELL = "sell"
    NO_SIGNAL = "no_signal"


@dataclass
class Signal:
    symbol: str | None = None
    timeframe: int | None = None
    strategy: str | None = None

    direction: SignalDirection = SignalDirection.NO_SIGNAL

    price_low: float | None = None
    price_high: float | None = None

    time: datetime | None = None

    score: float = 0.0
    distance: float = 0.0
    current_price: float | None = None

    reason: str | None = None

    orderblock: OrderBlock | None = None
    fvg: FVG | None = None