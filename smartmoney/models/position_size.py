from dataclasses import dataclass


@dataclass
class PositionSizePlan:

    balance: float

    risk_percent: float

    risk_amount: float

    stop_distance: float

    position_size: float