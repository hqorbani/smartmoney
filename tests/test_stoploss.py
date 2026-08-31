import pandas as pd

from smartmoney.analyzers.entry import EntryAnalyzer
from smartmoney.analyzers.fvg import FVGAnalyzer
from smartmoney.analyzers.orderblock import OrderBlockAnalyzer
from smartmoney.analyzers.signal import SignalAnalyzer
from smartmoney.analyzers.stoploss import StopLossAnalyzer
from smartmoney.core.context import MarketContext
from smartmoney.models.signal import SignalDirection
from smartmoney.models.entry import EntryPlan

def make_context(rows):
    df = pd.DataFrame(rows)
    df["time"] = pd.to_datetime(df["time"])

    return MarketContext(
        symbol="TEST",
        timeframe=15,
        df=df,
    )


def test_bullish_stop_loss_is_orderblock_low():

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

    context.df.loc[2, "high"] = 102
    context.df.loc[2, "low"] = 99
    context.df.loc[2, "close"] = 100

    EntryAnalyzer().analyze(context)
    StopLossAnalyzer().analyze(context)

    assert context.signal.direction == SignalDirection.BUY
    assert context.entry_plan is not None
    assert context.stop_loss_plan is not None

    assert context.stop_loss_plan.stop_loss == 98
    assert (
        context.stop_loss_plan.entry_plan
        is context.entry_plan
    )


def test_bearish_stop_loss_is_orderblock_high():

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

    context.df.loc[2, "high"] = 102
    context.df.loc[2, "low"] = 99
    context.df.loc[2, "close"] = 101

    EntryAnalyzer().analyze(context)
    StopLossAnalyzer().analyze(context)

    assert context.signal.direction == SignalDirection.SELL
    assert context.entry_plan is not None
    assert context.stop_loss_plan is not None

    assert context.stop_loss_plan.stop_loss == 103
    assert (
        context.stop_loss_plan.entry_plan
        is context.entry_plan
    )


def test_no_stop_loss_without_entry_plan():

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

    StopLossAnalyzer().analyze(context)

    assert context.stop_loss_plan is None

def test_no_stop_loss_when_bullish_stop_is_not_below_entry():

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
    assert len(context.orderblocks) == 1

    context.entry_plan = EntryPlan(
        entry_price=97,
        orderblock=context.orderblocks[0],
        fvg=context.fvgs[0],
    )

    StopLossAnalyzer().analyze(context)

    assert context.stop_loss_plan is None


def test_no_stop_loss_when_bearish_stop_is_not_above_entry():

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
    assert len(context.orderblocks) == 1

    context.entry_plan = EntryPlan(
        entry_price=104,
        orderblock=context.orderblocks[0],
        fvg=context.fvgs[0],
    )

    StopLossAnalyzer().analyze(context)

    assert context.stop_loss_plan is None