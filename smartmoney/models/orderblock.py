from dataclasses import dataclass

import pandas as pd

from smartmoney.models.fvg import FVG


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
    # FVG متناظر با این Order Block
    related_fvg: FVG | None = None

    mitigated: bool = False
    mitigation_index: int | None = None
    mitigation_time: pd.Timestamp | None = None