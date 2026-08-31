import pandas as pd

from smartmoney.analyzers.fvg import FVGAnalyzer
from smartmoney.analyzers.orderblock import OrderBlockAnalyzer
from smartmoney.core.context import MarketContext


def make_context(rows):
    df = pd.DataFrame(rows)
    df["time"] = pd.to_datetime(df["time"])

    return MarketContext(
        symbol="TEST",
        timeframe=15,
        df=df,
    )


def test_bullish_orderblock_is_detected():
    context = make_context([
        {
            "time": "2026-01-01 10:00",
            "open": 101,
            "high": 103,
            "low": 98,
            "close": 99,
        },
        {
            "time": "2026-01-01 10:15",
            "open": 99,
            "high": 108,
            "low": 99,
            "close": 107,
        },
        {
            "time": "2026-01-01 10:30",
            "open": 107,
            "high": 112,
            "low": 105,
            "close": 110,
        },
    ])

    FVGAnalyzer().analyze(context)
    OrderBlockAnalyzer().analyze(context)

    assert len(context.fvgs) == 1
    assert len(context.orderblocks) == 1

    ob = context.orderblocks[0]

    assert ob.bullish is True
    assert ob.index == 0
    assert ob.time == pd.Timestamp("2026-01-01 10:00")
    assert ob.open == 101
    assert ob.high == 103
    assert ob.low == 98
    assert ob.close == 99
    assert ob.related_fvg is context.fvgs[0]
    assert ob.mitigated is False


def test_bearish_orderblock_is_detected():
    context = make_context([
        {
            "time": "2026-01-01 10:00",
            "open": 99,
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
    ])

    FVGAnalyzer().analyze(context)
    OrderBlockAnalyzer().analyze(context)

    assert len(context.fvgs) == 1
    assert len(context.orderblocks) == 1

    ob = context.orderblocks[0]

    assert ob.bullish is False
    assert ob.index == 0
    assert ob.time == pd.Timestamp("2026-01-01 10:00")
    assert ob.open == 99
    assert ob.high == 103
    assert ob.low == 98
    assert ob.close == 102
    assert ob.related_fvg is context.fvgs[0]
    assert ob.mitigated is False