from dataclasses import dataclass
from enum import Enum


class StructureEventType(Enum):

    BULLISH_CONFIRMED = "BULLISH_CONFIRMED"

    BEARISH_CONFIRMED = "BEARISH_CONFIRMED"

    BULLISH_WEAKNESS = "BULLISH_WEAKNESS"

    BEARISH_WEAKNESS = "BEARISH_WEAKNESS"

    BOS = "BOS"

    CHOCH = "CHOCH"

    BULLISH_BOS = "BULLISH_BOS"

    BEARISH_BOS = "BEARISH_BOS"

    BULLISH_CHOCH = "BULLISH_CHOCH"

    BEARISH_CHOCH = "BEARISH_CHOCH"


@dataclass(slots=True)
class StructureEvent:

    type: StructureEventType