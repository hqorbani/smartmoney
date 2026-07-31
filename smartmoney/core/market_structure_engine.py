from smartmoney.core.context import MarketContext

from smartmoney.models.market_structure import (
    MarketBias,
)

from smartmoney.models.structure_event import (
    StructureEvent,
    StructureEventType,
)


class MarketStructureEngine:
    """
    Maintains market structure state.

    Responsibilities:

    - Market Bias
    - Protected Levels (future)
    - BOS (future)
    - CHOCH (future)

    This engine acts as a state machine.
    """

    # --------------------------------------------------

    def update(
        self,
        context: MarketContext,
        events: list[StructureEvent],
    ) -> None:

        structure = context.market_structure

        if structure.bias == MarketBias.UNKNOWN:

            self._handle_unknown(
                context,
                events,
            )

        elif structure.bias == MarketBias.BULLISH:

            self._handle_bullish(
                context,
                events,
            )

        elif structure.bias == MarketBias.BEARISH:

            self._handle_bearish(
                context,
                events,
            )

    # ==================================================
    # UNKNOWN
    # ==================================================

    def _handle_unknown(
        self,
        context: MarketContext,
        events: list[StructureEvent],
    ) -> None:

        structure = context.market_structure

        for event in events:

            if (
                event.type
                ==
                StructureEventType.BULLISH_CONFIRMED
            ):

                structure.bias = MarketBias.BULLISH

                self._initialize_bullish(
                    context,
                )

                return

            if (
                event.type
                ==
                StructureEventType.BEARISH_CONFIRMED
            ):

                structure.bias = MarketBias.BEARISH

                self._initialize_bearish(
                    context,
                )

                return

    # ==================================================
    # BULLISH
    # ==================================================

    def _handle_bullish(
        self,
        context: MarketContext,
        events: list[StructureEvent],
    ) -> None:

        structure = context.market_structure

        for event in events:

            if (
                event.type
                ==
                StructureEventType.BEARISH_WEAKNESS
            ):

                structure.bias = MarketBias.TRANSITION

                return

    # ==================================================
    # BEARISH
    # ==================================================

    def _handle_bearish(
        self,
        context: MarketContext,
        events: list[StructureEvent],
    ) -> None:

        structure = context.market_structure

        for event in events:

            if (
                event.type
                ==
                StructureEventType.BULLISH_WEAKNESS
            ):

                structure.bias = MarketBias.TRANSITION

                return

    # ==================================================
    # Initialization
    # ==================================================

    def _initialize_bullish(
        self,
        context: MarketContext,
    ) -> None:

        """
        Future:
        Set protected low.
        """

        pass

    # --------------------------------------------------

    def _initialize_bearish(
        self,
        context: MarketContext,
    ) -> None:

        """
        Future:
        Set protected high.
        """

        pass