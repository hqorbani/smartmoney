from smartmoney.core.context import MarketContext
from smartmoney.models.market_structure import MarketBias
from smartmoney.models.swing_relation import SwingRelationType


class MarketStructureEngine:
    """
    Computes the current market state from swing relations.
    """

    def update(
        self,
        context: MarketContext,
    ) -> None:

        structure = context.market_structure

        if not context.swing_relations:
            structure.bias = MarketBias.UNKNOWN
            return

        last = context.swing_relations[-1]

        match last.relation:

            case (
                SwingRelationType.HIGHER_HIGH
                | SwingRelationType.HIGHER_LOW
            ):
                structure.bias = MarketBias.BULLISH

            case (
                SwingRelationType.LOWER_HIGH
                | SwingRelationType.LOWER_LOW
            ):
                structure.bias = MarketBias.BEARISH

            case _:
                structure.bias = MarketBias.UNKNOWN
