from dataclasses import dataclass
from enum import Enum

import pandas as pd

from smartmoney.models.fvg import FVG


class Attempt1Status(Enum):
    NOT_USED = "NotUsed"
    SUCCESS = "Success"
    FAILED = "Failed"


class Attempt2Status(Enum):
    NOT_AVAILABLE = "NotAvailable"
    AVAILABLE = "Available"
    SUCCESS = "Success"
    FAILED = "Failed"


class OrderBlockStatus(Enum):
    ACTIVE = "Active"
    CONSUMED = "Consumed"


@dataclass(slots=True)
class OrderBlock:
    """
    ICT Order Block
    """

    index: int
    time: pd.Timestamp

    open: float
    high: float
    low: float
    close: float

    bullish: bool

    expanded_high: float | None = None
    expanded_low: float | None = None

    related_fvg: FVG | None = None

    mitigated: bool = False
    mitigation_index: int | None = None
    mitigation_time: pd.Timestamp | None = None

    attempt1_status: Attempt1Status = Attempt1Status.NOT_USED
    attempt2_status: Attempt2Status = Attempt2Status.NOT_AVAILABLE
    status: OrderBlockStatus = OrderBlockStatus.ACTIVE