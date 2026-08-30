from dataclasses import dataclass
from enum import Enum


class StrategyZoneState(Enum):
    AVAILABLE = "AVAILABLE"
    CONSUMED = "CONSUMED"


@dataclass(slots=True, frozen=True)
class StrategyZoneKey:
    """
    Stable identity of an OrderBlock for strategy purposes.
    """

    symbol: str
    timeframe: int
    time: str
    bullish: bool


@dataclass(slots=True)
class StrategyZone:
    """
    Tracks the lifecycle of an OrderBlock inside a strategy.
    """

    key: StrategyZoneKey

    state: StrategyZoneState = StrategyZoneState.AVAILABLE

    trade_count: int = 0