from dataclasses import dataclass
from enum import Enum


class StructureType(Enum):

    BOS = "BOS"

    CHOCH = "CHOCH"

    MSS = "MSS"


@dataclass(slots=True)
class Structure:

    index: int

    price: float

    bullish: bool

    type: StructureType