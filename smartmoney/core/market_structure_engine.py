from smartmoney.core.context import MarketContext

from smartmoney.models.market_structure import (
    MarketBias,
)

from smartmoney.models.structure_event import (
    StructureEvent,
    StructureEventType,
)

from smartmoney.models.swing_relation import (
    SwingRelationType,
)


class MarketStructureEngine:
    """
    Maintains ICT market structure state.

    Responsibilities

    - Market Bias
    - Protected Levels
    - BOS (future)
    - CHOCH (future)

    This engine is the single owner of
    MarketStructure state.
    """

    # --------------------------------------------------
    # Initial ICT patterns
    # --------------------------------------------------

    _INITIAL_BULLISH_PATTERN = (
        SwingRelationType.HIGHER_HIGH,
        SwingRelationType.HIGHER_LOW,
        SwingRelationType.HIGHER_HIGH,
    )

    _INITIAL_BEARISH_PATTERN = (
        SwingRelationType.LOWER_LOW,
        SwingRelationType.LOWER_HIGH,
        SwingRelationType.LOWER_LOW,
    )

    # ==================================================
    # Public
    # ==================================================

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

        elif structure.bias == MarketBias.TRANSITION:

            self._handle_transition(
                context,
                events,
            )
        # ---------- Debug ----------
        structure = context.market_structure

        print()
        print(context.symbol, context.timeframe)

        print("Bias:", structure.bias.name)

        print("Protected High :", structure.protected_high.price)

        print("Protected Low  :", structure.protected_low.price)

        print("Structural High:", structure.structural_high.price)

        print("Structural Low :", structure.structural_low.price)
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

            if event.type == StructureEventType.BULLISH_CONFIRMED:

                structure.bias = MarketBias.BULLISH

                self._initialize_bullish(
                    context,
                )

                return

            if event.type == StructureEventType.BEARISH_CONFIRMED:

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

            if event.type == StructureEventType.BEARISH_WEAKNESS:

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

            if event.type == StructureEventType.BULLISH_WEAKNESS:

                structure.bias = MarketBias.TRANSITION

                return

    # ==================================================
    # TRANSITION
    # ==================================================

    def _handle_transition(
        self,
        context: MarketContext,
        events: list[StructureEvent],
    ) -> None:

        """
        Future

        - CHOCH
        - MSS
        """

        pass

    # ==================================================
    # Initialization
    # ==================================================

    def _initialize_bullish(
        self,
        context: MarketContext,
    ) -> None:

        self._find_initial_protected_low(context)

        self._find_initial_structural_high(context)
    # --------------------------------------------------

    def _initialize_bearish(
        self,
        context: MarketContext,
    ) -> None:

        self._find_initial_protected_high(context)

        self._find_initial_structural_low(context)
    # ==================================================
    # Protected Levels
    # ==================================================

    def _find_initial_protected_low(
        self,
        context: MarketContext,
    ) -> None:

        relations = context.swing_relations

        structure = context.market_structure

        for i in range(len(relations) - 3, -1, -1):

            pattern = (
                relations[i].relation,
                relations[i + 1].relation,
                relations[i + 2].relation,
            )

            if pattern == self._INITIAL_BULLISH_PATTERN:

                swing = relations[i + 1].current

                structure.protected_low.price = swing.price
                structure.protected_low.swing_index = swing.index                

                return

    # --------------------------------------------------

    def _find_initial_protected_high(
        self,
        context: MarketContext,
    ) -> None:

        relations = context.swing_relations

        structure = context.market_structure

        for i in range(len(relations) - 3, -1, -1):

            pattern = (
                relations[i].relation,
                relations[i + 1].relation,
                relations[i + 2].relation,
            )

            if pattern == self._INITIAL_BEARISH_PATTERN:

                swing = relations[i + 1].current

                structure.protected_high.price = swing.price
                structure.protected_high.swing_index = swing.index

                return

    def _find_initial_structural_high(
        self,
        context: MarketContext,
    ) -> None:

        relations = context.swing_relations

        structure = context.market_structure

        for i in range(len(relations) - 3, -1, -1):

            pattern = (
                relations[i].relation,
                relations[i + 1].relation,
                relations[i + 2].relation,
            )

            if pattern == self._INITIAL_BULLISH_PATTERN:

                swing = relations[i + 2].current
                structure.structural_high.price = swing.price
                structure.structural_high.swing_index = swing.index

                return

    def _find_initial_structural_low(
        self,
        context: MarketContext,
    ) -> None:

        relations = context.swing_relations

        structure = context.market_structure

        for i in range(len(relations) - 3, -1, -1):

            pattern = (
                relations[i].relation,
                relations[i + 1].relation,
                relations[i + 2].relation,
            )

            if pattern == self._INITIAL_BEARISH_PATTERN:

                swing = relations[i + 2].current

                structure.structural_low.price = swing.price
                structure.structural_low.swing_index = swing.index

                return            
