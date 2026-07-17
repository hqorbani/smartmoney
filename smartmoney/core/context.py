from dataclasses import dataclass, field

import pandas as pd

from smartmoney.models.swing import Swing
from smartmoney.models.structure import Structure
from smartmoney.models.fvg import FVG
from smartmoney.models.orderblock import OrderBlock


@dataclass
class MarketContext:

    symbol: str

    timeframe: int

    df: pd.DataFrame

    last_candle_time: pd.Timestamp | None = None

    swings: list[Swing] = field(default_factory=list)

    structures: list[Structure] = field(default_factory=list)

    fvgs: list[FVG] = field(default_factory=list)

    orderblocks: list[OrderBlock] = field(default_factory=list)