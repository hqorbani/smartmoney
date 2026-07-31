from smartmoney.core.context import MarketContext

from smartmoney.models.structure_event import (
    StructureEvent,
    StructureEventType,
)

from smartmoney.models.swing_relation import (
    SwingRelation,
    SwingRelationType,
)
from smartmoney.config import Config

class StructureEventEngine:

    def run(
        self,
        context: MarketContext,
    ) -> list[StructureEvent]:

        events: list[StructureEvent] = []

        relations = context.swing_relations

        if self._is_bullish_confirmed(relations):

            events.append(
                StructureEvent(
                    type=StructureEventType.BULLISH_CONFIRMED,
                )
            )

        elif self._is_bearish_confirmed(relations):

            events.append(
                StructureEvent(
                    type=StructureEventType.BEARISH_CONFIRMED,
                )
            )

        elif self._is_bullish_weakness(relations):

            events.append(
                StructureEvent(
                    type=StructureEventType.BULLISH_WEAKNESS,
                )
            )

        elif self._is_bearish_weakness(relations):

            events.append(
                StructureEvent(
                    type=StructureEventType.BEARISH_WEAKNESS,
                )
            )

        return events

    # ---------------------------------------------------------

    def _is_bullish_confirmed(
        self,
        relations: list[SwingRelation],
    ) -> bool:

        return (
            self._find_pattern(
                relations,
                (
                    SwingRelationType.HIGHER_HIGH,
                    SwingRelationType.HIGHER_LOW,
                    SwingRelationType.HIGHER_HIGH,
                ),
            )
            is not None
        )

    # ---------------------------------------------------------

    def _is_bearish_confirmed(
        self,
        relations: list[SwingRelation],
    ) -> bool:

        return (
            self._find_pattern(
                relations,
                (
                    SwingRelationType.HIGHER_HIGH,
                    SwingRelationType.HIGHER_LOW,
                    SwingRelationType.HIGHER_HIGH,
                ),
            )
            is not None
        )

    # ---------------------------------------------------------

    def _is_bullish_weakness(
        self,
        relations: list[SwingRelation],
    ) -> bool:

        return (
            self._find_pattern(
                relations,
                (
                    SwingRelationType.HIGHER_HIGH,
                    SwingRelationType.HIGHER_LOW,
                    SwingRelationType.HIGHER_HIGH,
                ),
            )
            is not None
        )

    # ---------------------------------------------------------

    def _is_bearish_weakness(
        self,
        relations: list[SwingRelation],
    ) -> bool:

        return (
            self._find_pattern(
                relations,
                (
                    SwingRelationType.HIGHER_HIGH,
                    SwingRelationType.HIGHER_LOW,
                    SwingRelationType.HIGHER_HIGH,
                ),
            )
            is not None
        )

    # ---------------------------------------------------------
    def _find_pattern(
        self,
        relations: list[SwingRelation],
        pattern: tuple[SwingRelationType, ...],
    ) -> SwingRelation | None:

        length = len(pattern)

        if len(relations) < length:
            return None

        for i in range(
            len(relations) - length,
            -1,
            -1,
        ):

            current = tuple(
                relation.relation
                for relation in relations[i:i + length]
            )

            if current == pattern:

                #
                # Return the middle relation.
                #
                # HH HL HH -> HL
                # LL LH LL -> LH
                #

                return relations[i + 1]

        return None