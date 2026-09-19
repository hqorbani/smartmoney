from dataclasses import dataclass
from enum import Enum


class TradeDirection(Enum):
    BUY = "buy"
    SELL = "sell"


@dataclass(frozen=True, slots=True)
class TradePlan:
    """
    A complete trade plan produced from a trading signal.

    This object contains only the information required to execute
    or simulate a trade. It does not depend on MT5.
    """

    symbol: str
    timeframe: int

    direction: TradeDirection

    entry_price: float
    stop_loss: float
    take_profit: float

    risk_distance: float
    orderblock_index: int