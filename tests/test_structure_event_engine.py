
import pandas as pd
import pytest

from smartmoney.core.context import MarketContext
from smartmoney.core.structure_event_engine import StructureEventEngine
from smartmoney.models.structure_event import StructureEventType
from smartmoney.models.swing import Swing
from smartmoney.models.swing_relation import (
    SwingRelation,
    SwingRelationType,
)


def make_relations(
    relation_types: tuple[SwingRelationType, ...],
) -> list[SwingRelation]:
    relations = []

    for index, relation_type in enumerate(relation_types):
        previous = Swing(
            index=index * 2,
            time=pd.Timestamp("2024-01-01")
            + pd.Timedelta(minutes=index * 2),
            price=100.0 + index,
            is_high=relation_type
            in (
                SwingRelationType.HIGHER_HIGH,
                SwingRelationType.LOWER_HIGH,
            ),
        )

        current = Swing(
            index=index * 2 + 1,
            time=pd.Timestamp("2024-01-01")
            + pd.Timedelta(minutes=index * 2 + 1),
            price=101.0 + index,
            is_high=relation_type
            in (
                SwingRelationType.HIGHER_HIGH,
                SwingRelationType.LOWER_HIGH,
            ),
        )

        relations.append(
            SwingRelation(
                previous=previous,
                current=current,
                relation=relation_type,
            )
        )

    return relations


@pytest.mark.parametrize(
    ("relations", "expected_event"),
    [
        (
            (
                SwingRelationType.HIGHER_HIGH,
                SwingRelationType.HIGHER_LOW,
                SwingRelationType.HIGHER_HIGH,
            ),
            StructureEventType.BULLISH_CONFIRMED,
        ),
        (
            (
                SwingRelationType.LOWER_LOW,
                SwingRelationType.LOWER_HIGH,
                SwingRelationType.LOWER_LOW,
            ),
            StructureEventType.BEARISH_CONFIRMED,
        ),
        (
            (
                SwingRelationType.HIGHER_HIGH,
                SwingRelationType.HIGHER_LOW,
                SwingRelationType.LOWER_HIGH,
            ),
            StructureEventType.BEARISH_WEAKNESS,
        ),
        (
            (
                SwingRelationType.LOWER_LOW,
                SwingRelationType.LOWER_HIGH,
                SwingRelationType.HIGHER_LOW,
            ),
            StructureEventType.BULLISH_WEAKNESS,
        ),
    ],
)
def test_run_detects_expected_structure_event(
    relations: tuple[SwingRelationType, ...],
    expected_event: StructureEventType,
) -> None:
    context = MarketContext(
        symbol="TEST",
        timeframe=5,
        df=pd.DataFrame(),
        swing_relations=make_relations(relations),
    )

    events = StructureEventEngine().run(context)

    assert [event.type for event in events] == [expected_event]


def test_run_returns_no_event_with_fewer_than_three_relations() -> None:
    context = MarketContext(
        symbol="TEST",
        timeframe=5,
        df=pd.DataFrame(),
        swing_relations=make_relations(
            (
                SwingRelationType.HIGHER_HIGH,
                SwingRelationType.HIGHER_LOW,
            )
        ),
    )

    events = StructureEventEngine().run(context)

    assert events == []
