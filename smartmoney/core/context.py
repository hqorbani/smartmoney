from dataclasses import dataclass, field

import pandas as pd

from smartmoney.models.swing import Swing
from smartmoney.models.structure import Structure
from smartmoney.models.fvg import FVG
from smartmoney.models.orderblock import OrderBlock
from smartmoney.models.market_structure import MarketStructure
from smartmoney.models.swing_relation import SwingRelation
from smartmoney.models.signal import Signal
from smartmoney.models.entry import EntryPlan
from smartmoney.models.stoploss import StopLossPlan
from smartmoney.models.takeprofit import TakeProfitPlan

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

    signal: Signal = field(
        default_factory=Signal
    )
    entry_plan: EntryPlan | None = None
    stop_loss_plan: StopLossPlan | None = None
    take_profit_plan: TakeProfitPlan | None = None
    market_structure: MarketStructure = field(
        default_factory=MarketStructure
    )

    swing_relations: list[SwingRelation] = field(
        default_factory=list
    )