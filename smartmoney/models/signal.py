from dataclasses import dataclass
from enum import Enum

from smartmoney.models.fvg import FVG
from smartmoney.models.orderblock import OrderBlock


class SignalDirection(str, Enum):
    BUY = "buy"
    SELL = "sell"
    NO_SIGNAL = "no_signal"


@dataclass
class Signal:
    direction: SignalDirection = SignalDirection.NO_SIGNAL

    reason: str | None = None

    orderblock: OrderBlock | None = None

    fvg: FVG | None = None