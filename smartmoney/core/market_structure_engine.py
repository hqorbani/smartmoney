from smartmoney.core.context import MarketContext
from smartmoney.models.market_structure import (
    MarketBias,
)
from smartmoney.models.swing_relation import (
    SwingRelation,
    SwingRelationType,
)


class MarketStructureEngine:
    """
    Infers the current market structure
    from swing relations.
    """

    def update(
        self,
        context: MarketContext,
    ) -> None:

        structure = context.market_structure

        relations = context.swing_relations

        if self._is_initial_bullish(relations):

            structure.bias = MarketBias.BULLISH

            return

        if self._is_initial_bearish(relations):

            structure.bias = MarketBias.BEARISH

            return

        structure.bias = MarketBias.UNKNOWN

    # ---------------------------------------------------------

    def _is_initial_bullish(
        self,
        relations: list[SwingRelation],
    ) -> bool:

        if len(relations) < 3:

            return False

        pattern = [

            relations[-3].relation,

            relations[-2].relation,

            relations[-1].relation,

        ]

        return pattern == [

            SwingRelationType.HIGHER_HIGH,

            SwingRelationType.HIGHER_LOW,

            SwingRelationType.HIGHER_HIGH,

        ]

    # ---------------------------------------------------------

    def _is_initial_bearish(
        self,
        relations: list[SwingRelation],
    ) -> bool:

        if len(relations) < 3:

            return False

        pattern = [

            relations[-3].relation,

            relations[-2].relation,

            relations[-1].relation,

        ]

        return pattern == [

            SwingRelationType.LOWER_LOW,

            SwingRelationType.LOWER_HIGH,

            SwingRelationType.LOWER_LOW,

        ]