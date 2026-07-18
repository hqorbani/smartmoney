from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass(slots=True)
class Signal:

    # ---------------------------------
    # Identity
    # ---------------------------------

    id: str = field(
        default_factory=lambda: str(uuid4())
    )

    # ---------------------------------
    # Market
    # ---------------------------------

    symbol: str = ""

    timeframe: int = 0

    strategy: str = ""

    direction: str = ""

    # ---------------------------------
    # Zone
    # ---------------------------------

    price_low: float = 0.0

    price_high: float = 0.0

    # ---------------------------------
    # Times
    # ---------------------------------

    time: datetime = field(
        default_factory=datetime.utcnow
    )

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )

    # ---------------------------------
    # Live Market
    # ---------------------------------

    current_price: float = 0.0

    distance: float = 0.0

    # ---------------------------------
    # Ranking
    # ---------------------------------

    score: float = 0.0

    rank: int = 0

    # ---------------------------------
    # Status
    # ---------------------------------

    status: str = "ACTIVE"