from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class PositionSize:
    """
    Calculated position size for a trade.

    The actual broker-specific interpretation of this value
    will be handled later by the execution layer.
    """

    risk_amount: float
    risk_distance: float
    size: float
    