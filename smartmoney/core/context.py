from dataclasses import dataclass, field

import pandas as pd

from smartmoney.models.swing import Swing
from smartmoney.models.structure import Structure
from smartmoney.models.fvg import FVG
from smartmoney.models.orderblock import OrderBlock
from smartmoney.models.market_structure import MarketStructure
from smartmoney.models.swing_relation import SwingRelation
from smartmoney.models.structure_event import StructureEvent
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

    market_structure: MarketStructure = field(
        default_factory=MarketStructure
    )

    swing_relations: list[SwingRelation] = field(
        default_factory=list
    )

    structure_events: list[StructureEvent] = field(
        default_factory=list
    )