import pandas as pd

from smartmoney.analyzers.fvg import FVGAnalyzer
from smartmoney.analyzers.orderblock import OrderBlockAnalyzer
from smartmoney.analyzers.signal import SignalAnalyzer
from smartmoney.core.context import MarketContext
from smartmoney.models.signal import SignalDirection


def make_context(rows):
    df = pd.DataFrame(rows)
    df["time"] = pd.to_datetime(df["time"])

    return MarketContext(
        symbol="TEST",
        timeframe=15,
        df=df,
    )


def test_bullish_signal_is_generated():

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
    SignalAnalyzer().analyze(context)

    assert context.signal.direction == SignalDirection.BUY
    assert context.signal.orderblock is context.orderblocks[0]
    assert context.signal.fvg is context.fvgs[0]


def test_bearish_signal_is_generated():

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
    SignalAnalyzer().analyze(context)

    assert context.signal.direction == SignalDirection.SELL
    assert context.signal.orderblock is context.orderblocks[0]
    assert context.signal.fvg is context.fvgs[0]

def test_no_signal_when_no_orderblock_exists():

    context = make_context([
        {
            "time": "2026-01-01 10:00",
            "open": 100,
            "high": 101,
            "low": 99,
            "close": 100,
        },
        {
            "time": "2026-01-01 10:15",
            "open": 100,
            "high": 101,
            "low": 99,
            "close": 100,
        },
        {
            "time": "2026-01-01 10:30",
            "open": 100,
            "high": 101,
            "low": 99,
            "close": 100,
        },
    ])

    SignalAnalyzer().analyze(context)

    assert context.signal.direction == SignalDirection.NO_SIGNAL
    assert context.signal.orderblock is None
    assert context.signal.fvg is None    