from dataclasses import dataclass
from enum import Enum

import pandas as pd


class FVGStatus(Enum):
    ACTIVE = "active"
    MITIGATED = "mitigated"
    FILLED = "filled"


@dataclass(slots=True)
class FVG:
    start_index: int
    end_index: int

    start_time: pd.Timestamp
    end_time: pd.Timestamp

    high: float
    low: float

    bullish: bool

    status: FVGStatus = FVGStatus.ACTIVE

    mitigation_index: int | None = None
    mitigation_time: pd.Timestamp | None = None