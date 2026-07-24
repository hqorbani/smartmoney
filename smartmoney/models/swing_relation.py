from dataclasses import dataclass
from enum import Enum

from smartmoney.models.swing import Swing


class SwingRelationType(Enum):

    HIGHER_HIGH = "HH"

    HIGHER_LOW = "HL"

    LOWER_HIGH = "LH"

    LOWER_LOW = "LL"


@dataclass(slots=True)
class SwingRelation:

    swing: Swing

    relation: SwingRelationType