from dataclasses import dataclass, field
from enum import Enum

from smartmoney.models.structure_level import StructureLevel


class MarketBias(Enum):
    UNKNOWN = "UNKNOWN"
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    TRANSITION = "TRANSITION"


@dataclass(slots=True)
class MarketStructure:
    """
    Represents current ICT market structure state.

    Pure data model.

    All business logic belongs to
    MarketStructureEngine.
    """

    # --------------------------------------------------
    # Current Bias
    # --------------------------------------------------

    bias: MarketBias = MarketBias.UNKNOWN

    # --------------------------------------------------
    # Statistics
    # --------------------------------------------------

    bos_count: int = 0

    choch_count: int = 0

    # --------------------------------------------------
    # ICT Levels
    # --------------------------------------------------

    protected_high: StructureLevel = field(
        default_factory=StructureLevel,
    )

    protected_low: StructureLevel = field(
        default_factory=StructureLevel,
    )

    structural_high: StructureLevel = field(
        default_factory=StructureLevel,
    )

    structural_low: StructureLevel = field(
        default_factory=StructureLevel,
    )