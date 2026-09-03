import pandas as pd
import pytest

from smartmoney.backtesting.orderblock_zones import OrderBlockDepthZone
from smartmoney.backtesting.runner import HistoricalBacktestRunner
from smartmoney.models.fvg import FVG
from smartmoney.models.orderblock import OrderBlock


def make_orderblock(
    *,
    bullish: bool,
    confirmation_index: int = 1,
) -> OrderBlock:
    fvg = FVG(
        start_index=0,
        end_index=confirmation_index,
        start_time=pd.Timestamp("2026-01-01"),
        end_time=pd.Timestamp("2026-01-01 00:01"),
        high=100.0,
        low=95.0,
        bullish=bullish,
    )

    return OrderBlock(
        index=0,
        time=pd.Timestamp("2026-01-01"),
        open=97.0,
        high=100.0,
        low=90.0,
        close=95.0,
        bullish=bullish,
        related_fvg=fvg,
    )


def make_data() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "time": pd.Timestamp("2026-01-01 00:00"),
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
                "close": 100.0,
            },
            {
                "time": pd.Timestamp("2026-01-01 00:01"),
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
                "close": 100.0,
            },
            {
                "time": pd.Timestamp("2026-01-01 00:02"),
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
                "close": 100.0,
            },
        ]
    )


def test_empty_dataframe_returns_no_results():
    runner = HistoricalBacktestRunner("TEST", 1)

    result = runner.run(
        pd.DataFrame(columns=["open", "high", "low", "close"])
    )

    assert result == []


def test_missing_ohlc_columns_are_rejected():
    runner = HistoricalBacktestRunner("TEST", 1)

    df = pd.DataFrame(
        [
            {
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
            }
        ]
    )

    with pytest.raises(ValueError, match="close"):
        runner.run(df)


def test_touch_is_only_checked_from_confirmation_forward():
    ob = make_orderblock(bullish=True, confirmation_index=1)

    candle_before_confirmation = pd.Series(
        {"low": 91.0, "high": 101.0}
    )

    candle_at_confirmation = pd.Series(
        {"low": 101.0, "high": 102.0}
    )

    candle_after_confirmation = pd.Series(
        {"low": 98.0, "high": 101.0}
    )

    assert runner_touch(candle_before_confirmation, ob) is not None
    assert runner_touch(candle_at_confirmation, ob) is None

    touch = runner_touch(candle_after_confirmation, ob)

    assert touch is not None
    assert touch[0] is OrderBlockDepthZone.FIRST
    assert touch[1] == pytest.approx(0.2)


def test_bullish_touch_uses_low_for_penetration():
    runner = HistoricalBacktestRunner("TEST", 1)
    ob = make_orderblock(bullish=True)

    touch = runner._check_touch(
        pd.Series({"low": 94.0, "high": 101.0}),
        ob,
    )

    assert touch is not None
    assert touch[0] is OrderBlockDepthZone.MIDDLE
    assert touch[1] == pytest.approx(0.6)


def test_bearish_touch_uses_high_for_penetration():
    runner = HistoricalBacktestRunner("TEST", 1)
    ob = make_orderblock(bullish=False)

    touch = runner._check_touch(
        pd.Series({"low": 89.0, "high": 96.0}),
        ob,
    )

    assert touch is not None
    assert touch[0] is OrderBlockDepthZone.MIDDLE
    assert touch[1] == pytest.approx(0.6)


def test_no_touch_returns_none():
    runner = HistoricalBacktestRunner("TEST", 1)
    ob = make_orderblock(bullish=True)

    touch = runner._check_touch(
        pd.Series({"low": 101.0, "high": 103.0}),
        ob,
    )

    assert touch is None


def test_full_candle_penetration_is_final_zone():
    runner = HistoricalBacktestRunner("TEST", 1)
    ob = make_orderblock(bullish=True)

    touch = runner._check_touch(
        pd.Series({"low": 85.0, "high": 105.0}),
        ob,
    )

    assert touch is not None
    assert touch[0] is OrderBlockDepthZone.FINAL
    assert touch[1] == pytest.approx(1.0)


def runner_touch(
    candle: pd.Series,
    ob: OrderBlock,
):
    runner = HistoricalBacktestRunner("TEST", 1)
    return runner._check_touch(candle, ob)