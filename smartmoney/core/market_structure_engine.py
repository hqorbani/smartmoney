from smartmoney.core.context import MarketContext
from smartmoney.models.market_structure import (
    MarketBias,
)
from smartmoney.models.swing_relation import (
    SwingRelation,
    SwingRelationType,
)

from smartmoney.models.structure_event import (
    StructureEvent,
    StructureEventType,
)



class MarketStructureEngine:
    """
    Infers the current market structure
    from swing relations.
    """

    def update(
        self,
        context: MarketContext,
        events: list[StructureEvent],
    ) -> None:

        structure = context.market_structure

        structure.bias = MarketBias.UNKNOWN

        for event in events:

            if event.type == StructureEventType.BULLISH_CONFIRMED:

                structure.bias = MarketBias.BULLISH

            elif event.type == StructureEventType.BEARISH_CONFIRMED:

                structure.bias = MarketBias.BEARISH
    # ---------------------------------------------------------
