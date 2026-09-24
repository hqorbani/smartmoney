from dataclasses import dataclass

from smartmoney.models.fvg import FVG
from smartmoney.models.orderblock import OrderBlock


@dataclass
class EntryZone:

    name: str

    price_low: float
    price_high: float


@dataclass
class EntryPlan:

    entry_price: float

    orderblock: OrderBlock

    fvg: FVG

    zones: list[EntryZone]