from smartmoney.services.zone_entry_service import (
    ZoneEntryService,
    ZoneEntryState,
)


def test_first_entry_happens_only_once_while_price_stays_inside():
    service = ZoneEntryService()
    state = ZoneEntryState()

    assert service.is_first_entry(state, 99.0, 100.0, 110.0) is False
    assert service.is_first_entry(state, 100.0, 100.0, 110.0) is True
    assert service.is_first_entry(state, 105.0, 100.0, 110.0) is False
    assert service.is_first_entry(state, 110.0, 100.0, 110.0) is False


def test_reentry_after_leaving_zone_triggers_again():
    service = ZoneEntryService()
    state = ZoneEntryState()

    assert service.is_first_entry(state, 105.0, 100.0, 110.0) is True
    assert service.is_first_entry(state, 105.0, 100.0, 110.0) is False

    assert service.is_first_entry(state, 95.0, 100.0, 110.0) is False

    assert service.is_first_entry(state, 105.0, 100.0, 110.0) is True