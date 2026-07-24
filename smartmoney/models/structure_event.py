from dataclasses import dataclass
from enum import Enum


class StructureEventType(Enum):

    BULLISH_CONFIRMED = "BULLISH_CONFIRMED"

    BEARISH_CONFIRMED = "BEARISH_CONFIRMED"

    BULLISH_WEAKNESS = "BULLISH_WEAKNESS"

    BEARISH_WEAKNESS = "BEARISH_WEAKNESS"

    BOS = "BOS"

    CHOCH = "CHOCH"


@dataclass(slots=True)
class StructureEvent:

    type: StructureEventType