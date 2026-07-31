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
    Represents the current market structure state.

    This model is intentionally passive and contains
    no business logic.

    All state transitions are handled by
    MarketStructureEngine.
    """

    # --------------------------------------------------
    # Current market bias
    # --------------------------------------------------

    bias: MarketBias = MarketBias.UNKNOWN

    # --------------------------------------------------
    # Statistics
    # --------------------------------------------------

    bos_count: int = 0

    choch_count: int = 0

    # --------------------------------------------------
    # ICT Protected Levels
    # --------------------------------------------------

    protected_high: float | None = None

    protected_low: float | None = None

    protected_high_swing_index: int | None = None

    protected_low_swing_index: int | None = None