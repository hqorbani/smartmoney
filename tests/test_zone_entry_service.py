import pandas as pd

from smartmoney.models.orderblock import OrderBlock
from smartmoney.services.zone_entry_service import ZoneEntryService


def create_orderblock() -> OrderBlock:
    return OrderBlock(
        index=1,
        time=pd.Timestamp("2026-01-01"),
        open=100.0,
        high=105.0,
        low=95.0,
        close=102.0,
        bullish=True,
    )


def test_initial_zone_first_entry_happens_only_once_while_price_stays_inside():
    service = ZoneEntryService()
    orderblock = create_orderblock()

    assert service.is_first_entry(
        orderblock, "INITIAL", 99.0, 100.0, 110.0
    ) is False
    assert service.is_first_entry(
        orderblock, "INITIAL", 100.0, 100.0, 110.0
    ) is True
    assert service.is_first_entry(
        orderblock, "INITIAL", 105.0, 100.0, 110.0
    ) is False
    assert service.is_first_entry(
        orderblock, "INITIAL", 110.0, 100.0, 110.0
    ) is False


def test_initial_zone_reentry_after_leaving_triggers_again():
    service = ZoneEntryService()
    orderblock = create_orderblock()

    assert service.is_first_entry(
        orderblock, "INITIAL", 105.0, 100.0, 110.0
    ) is True
    assert service.is_first_entry(
        orderblock, "INITIAL", 105.0, 100.0, 110.0
    ) is False

    assert service.is_first_entry(
        orderblock, "INITIAL", 95.0, 100.0, 110.0
    ) is False

    assert service.is_first_entry(
        orderblock, "INITIAL", 105.0, 100.0, 110.0
    ) is True


def test_middle_zone_uses_its_own_entry_state():
    service = ZoneEntryService()
    orderblock = create_orderblock()

    assert service.is_first_entry(
        orderblock, "MIDDLE", 105.0, 100.0, 110.0
    ) is True
    assert service.is_first_entry(
        orderblock, "MIDDLE", 106.0, 100.0, 110.0
    ) is False

    assert orderblock.initial_zone_inside is False
    assert orderblock.middle_zone_inside is True


def test_unsupported_zone_raises_error():
    service = ZoneEntryService()
    orderblock = create_orderblock()

    try:
        service.is_first_entry(
            orderblock, "FINAL", 105.0, 100.0, 110.0
        )
    except ValueError as exc:
        assert str(exc) == "Unsupported zone: FINAL"
    else:
        raise AssertionError("Expected ValueError")