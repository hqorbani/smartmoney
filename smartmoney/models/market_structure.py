from dataclasses import dataclass
from enum import Enum


class MarketBias(Enum):
    UNKNOWN = "UNKNOWN"
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    TRANSITION = "TRANSITION"


@dataclass(slots=True)
class MarketStructure:
    """
    Holds the current structural state of the market.

    This object is intentionally passive.
    It contains no business logic.

    MarketStructureEngine will be responsible for
    updating this object.
    """

    bias: MarketBias = MarketBias.UNKNOWN

    bos_count: int = 0

    choch_count: int = 0