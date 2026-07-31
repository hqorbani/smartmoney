from dataclasses import dataclass

import pandas as pd


@dataclass(slots=True)
class Swing:
    """
    Represents a swing high or swing low.
    """

    index: int

    time: pd.Timestamp

    price: float

    is_high: bool

    is_valid: bool = True

    is_broken: bool = False