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

        return self._match_pattern(
            relations,
            [
                SwingRelationType.HIGHER_HIGH,
                SwingRelationType.HIGHER_LOW,
                SwingRelationType.HIGHER_HIGH,
            ],
        )

    # ---------------------------------------------------------

    def _is_bearish_confirmed(
        self,
        relations: list[SwingRelation],
    ) -> bool:

        return self._match_pattern(
            relations,
            [
                SwingRelationType.LOWER_LOW,
                SwingRelationType.LOWER_HIGH,
                SwingRelationType.LOWER_LOW,
            ],
        )

    # ---------------------------------------------------------

    def _is_bullish_weakness(
        self,
        relations: list[SwingRelation],
    ) -> bool:

        return self._match_pattern(
            relations,
            [
                SwingRelationType.HIGHER_HIGH,
                SwingRelationType.HIGHER_LOW,
                SwingRelationType.LOWER_HIGH,
            ],
        )

    # ---------------------------------------------------------

    def _is_bearish_weakness(
        self,
        relations: list[SwingRelation],
    ) -> bool:

        return self._match_pattern(
            relations,
            [
                SwingRelationType.LOWER_LOW,
                SwingRelationType.LOWER_HIGH,
                SwingRelationType.HIGHER_LOW,
            ],
        )

    # ---------------------------------------------------------
    def _match_pattern(
        self,
        relations: list[SwingRelation],
        pattern: list[SwingRelationType],
    ) -> bool:

        if len(relations) < len(pattern):

            return False

        recent = [
            relation.relation
            for relation in relations[-len(pattern):]
        ]

        return recent == pattern