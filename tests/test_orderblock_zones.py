import pandas as pd
import pytest

from smartmoney.backtesting.orderblock_zones import (
    OrderBlockDepthZone,
    find_first_touch,
    zone_boundaries,
)
from smartmoney.models.fvg import FVG
from smartmoney.models.orderblock import OrderBlock


def make_orderblock(
    *,
    bullish: bool,
    high: float = 100.0,
    low: float = 90.0,
    related_fvg: FVG | None = None,
) -> OrderBlock:
    return OrderBlock(
        index=0,
        time=pd.Timestamp("2026-01-01"),
        open=95.0,
        high=high,
        low=low,
        close=95.0,
        bullish=bullish,
        related_fvg=related_fvg,
    )


def test_bullish_orderblock_zones_are_oriented_from_high_to_low():
    ob = make_orderblock(bullish=True)

    zones = zone_boundaries(ob)

    assert zones[OrderBlockDepthZone.FIRST] == pytest.approx(
        (96.6666666667, 100.0)
    )
    assert zones[OrderBlockDepthZone.MIDDLE] == pytest.approx(
        (93.3333333333, 96.6666666667)
    )
    assert zones[OrderBlockDepthZone.FINAL] == pytest.approx(
        (90.0, 93.3333333333)
    )


def test_bearish_orderblock_zones_are_oriented_from_low_to_high():
    ob = make_orderblock(bullish=False)

    zones = zone_boundaries(ob)

    assert zones[OrderBlockDepthZone.FIRST] == pytest.approx(
        (90.0, 93.3333333333)
    )
    assert zones[OrderBlockDepthZone.MIDDLE] == pytest.approx(
        (93.3333333333, 96.6666666667)
    )
    assert zones[OrderBlockDepthZone.FINAL] == pytest.approx(
        (96.6666666667, 100.0)
    )


def test_bullish_first_touch_is_classified_as_first_zone():
    df = pd.DataFrame(
        [
            {"low": 101.0, "high": 103.0},
            {"low": 98.0, "high": 101.0},
        ]
    )
    ob = make_orderblock(bullish=True)

    touch = find_first_touch(df, ob, start_index=1)

    assert touch is not None
    assert touch.index == 1
    assert touch.zone is OrderBlockDepthZone.FIRST
    assert touch.penetration == pytest.approx(0.2)


def test_bearish_first_touch_is_classified_as_first_zone():
    df = pd.DataFrame(
        [
            {"low": 87.0, "high": 89.0},
            {"low": 89.0, "high": 92.0},
        ]
    )
    ob = make_orderblock(bullish=False)

    touch = find_first_touch(df, ob, start_index=1)

    assert touch is not None
    assert touch.index == 1
    assert touch.zone is OrderBlockDepthZone.FIRST
    assert touch.penetration == pytest.approx(0.2)


def test_touch_crossing_multiple_zones_returns_deepest_zone_reached():
    df = pd.DataFrame(
        [
            {"low": 91.0, "high": 101.0},
        ]
    )
    ob = make_orderblock(bullish=True)

    touch = find_first_touch(df, ob, start_index=0)

    assert touch is not None
    assert touch.zone is OrderBlockDepthZone.FINAL
    assert touch.penetration == pytest.approx(0.9)


def test_returns_none_when_price_never_touches_orderblock():
    df = pd.DataFrame(
        [
            {"low": 101.0, "high": 103.0},
            {"low": 102.0, "high": 104.0},
        ]
    )
    ob = make_orderblock(bullish=True)

    assert find_first_touch(df, ob, start_index=0) is None


def test_candles_before_start_index_are_ignored():
    df = pd.DataFrame(
        [
            {"low": 95.0, "high": 101.0},
            {"low": 102.0, "high": 104.0},
            {"low": 97.0, "high": 101.0},
        ]
    )
    ob = make_orderblock(bullish=True)

    touch = find_first_touch(df, ob, start_index=2)

    assert touch is not None
    assert touch.index == 2


def test_default_start_index_uses_related_fvg_end_index():
    fvg = FVG(
        start_index=0,
        end_index=1,
        start_time=pd.Timestamp("2026-01-01"),
        end_time=pd.Timestamp("2026-01-01 00:01"),
        high=100.0,
        low=95.0,
        bullish=True,
    )
    ob = make_orderblock(bullish=True, related_fvg=fvg)

    df = pd.DataFrame(
        [
            {"low": 95.0, "high": 101.0},
            {"low": 96.0, "high": 101.0},
            {"low": 98.0, "high": 101.0},
        ]
    )

    touch = find_first_touch(df, ob)

    assert touch is not None
    assert touch.index == 2


def test_invalid_orderblock_range_is_rejected():
    ob = make_orderblock(bullish=True, high=90.0, low=100.0)

    with pytest.raises(ValueError):
        zone_boundaries(ob)


def test_missing_start_index_without_related_fvg_is_rejected():
    ob = make_orderblock(bullish=True)
    df = pd.DataFrame([{"low": 95.0, "high": 101.0}])

    with pytest.raises(ValueError):
        find_first_touch(df, ob)