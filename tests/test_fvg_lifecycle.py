import pandas as pd

from smartmoney.analyzers.fvg import FVGAnalyzer
from smartmoney.analyzers.fvg_lifecycle import FVGLifecycleAnalyzer
from smartmoney.core.context import MarketContext


def make_context(rows):
    df = pd.DataFrame(rows)
    df["time"] = pd.to_datetime(df["time"])

    return MarketContext(
        symbol="TEST",
        timeframe=15,
        df=df,
    )


def test_bullish_fvg_is_created_and_not_filled_initially():

    context = make_context([
        {
            "time": "2026-01-01 10:00",
            "open": 100,
            "high": 102,
            "low": 99,
            "close": 101,
        },
        {
            "time": "2026-01-01 10:15",
            "open": 101,
            "high": 108,
            "low": 101,
            "close": 107,
        },
        {
            "time": "2026-01-01 10:30",
            "open": 107,
            "high": 112,
            "low": 105,
            "close": 110,
        },
        {
            "time": "2026-01-01 10:45",
            "open": 110,
            "high": 113,
            "low": 108,
            "close": 112,
        },
    ])

    FVGAnalyzer().analyze(context)

    assert len(context.fvgs) == 1

    fvg = context.fvgs[0]

    assert fvg.bullish is True
    assert fvg.filled is False
    assert fvg.fill_index is None
    assert fvg.fill_time is None


def test_bullish_fvg_is_filled_when_price_enters_zone():

    context = make_context([
        {
            "time": "2026-01-01 10:00",
            "open": 100,
            "high": 102,
            "low": 99,
            "close": 101,
        },
        {
            "time": "2026-01-01 10:15",
            "open": 101,
            "high": 108,
            "low": 101,
            "close": 107,
        },
        {
            "time": "2026-01-01 10:30",
            "open": 107,
            "high": 112,
            "low": 105,
            "close": 110,
        },
        {
            "time": "2026-01-01 10:45",
            "open": 110,
            "high": 113,
            "low": 108,
            "close": 112,
        },
        {
            "time": "2026-01-01 11:00",
            "open": 112,
            "high": 113,
            "low": 102,
            "close": 105,
        },
    ])

    FVGAnalyzer().analyze(context)
    FVGLifecycleAnalyzer().analyze(context)

    assert len(context.fvgs) == 1

    fvg = context.fvgs[0]

    assert fvg.bullish is True
    assert fvg.filled is True
    assert fvg.fill_index == 4
    assert fvg.fill_time == pd.Timestamp("2026-01-01 11:00")


def test_bearish_fvg_is_filled_when_price_enters_zone():

    context = make_context([
        {
            "time": "2026-01-01 10:00",
            "open": 100,
            "high": 103,
            "low": 98,
            "close": 102,
        },
        {
            "time": "2026-01-01 10:15",
            "open": 102,
            "high": 102,
            "low": 93,
            "close": 94,
        },
        {
            "time": "2026-01-01 10:30",
            "open": 94,
            "high": 96,
            "low": 90,
            "close": 91,
        },
        {
            "time": "2026-01-01 10:45",
            "open": 91,
            "high": 94,
            "low": 87,
            "close": 89,
        },
        {
            "time": "2026-01-01 11:00",
            "open": 89,
            "high": 101,
            "low": 88,
            "close": 99,
        },
    ])

    FVGAnalyzer().analyze(context)
    FVGLifecycleAnalyzer().analyze(context)

    assert len(context.fvgs) == 1

    fvg = context.fvgs[0]

    assert fvg.bullish is False
    assert fvg.filled is True
    assert fvg.fill_index == 4
    assert fvg.fill_time == pd.Timestamp("2026-01-01 11:00")


def test_fvg_fill_is_not_recorded_before_formation():

    context = make_context([
        {
            "time": "2026-01-01 10:00",
            "open": 100,
            "high": 102,
            "low": 99,
            "close": 101,
        },
        {
            "time": "2026-01-01 10:15",
            "open": 101,
            "high": 108,
            "low": 101,
            "close": 107,
        },
        {
            "time": "2026-01-01 10:30",
            "open": 107,
            "high": 112,
            "low": 105,
            "close": 110,
        },
        {
            "time": "2026-01-01 10:45",
            "open": 110,
            "high": 113,
            "low": 108,
            "close": 112,
        },
    ])

    FVGAnalyzer().analyze(context)

    fvg = context.fvgs[0]

    assert fvg.filled is False
    assert fvg.fill_index is None
    assert fvg.fill_time is None