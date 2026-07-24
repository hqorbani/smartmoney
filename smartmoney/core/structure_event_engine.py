from smartmoney.core.context import MarketContext
from smartmoney.models.structure_event import (
    StructureEvent,
    StructureEventType,
)
from smartmoney.models.swing_relation import (
    SwingRelation,
    SwingRelationType,
)


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

        return events

    # ---------------------------------------------------------

    def _is_bullish_confirmed(
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

    def _is_bearish_confirmed(
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