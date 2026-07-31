from dataclasses import dataclass


@dataclass(slots=True)
class StructureLevel:
    """
    Represents a structural price level.

    Examples

    - Protected High
    - Protected Low
    - Structural High
    - Structural Low
    """

    price: float | None = None

    swing_index: int | None = None