from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Signal:

    symbol: str

    timeframe: int

    strategy: str

    direction: str

    price_low: float

    price_high: float

    time: datetime

    score: float = 0.0