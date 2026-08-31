import pandas as pd

from smartmoney.analyzers.entry import EntryAnalyzer
from smartmoney.analyzers.fvg import FVGAnalyzer
from smartmoney.analyzers.orderblock import OrderBlockAnalyzer
from smartmoney.analyzers.signal import SignalAnalyzer
from smartmoney.analyzers.stoploss import StopLossAnalyzer
from smartmoney.analyzers.takeprofit import TakeProfitAnalyzer
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


def prepare_bullish_context():

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

    return context


def prepare_bearish_context():

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

    return context


def test_bullish_take_profit_uses_two_to_one_risk_reward():

    context = prepare_bullish_context()

    assert context.signal.direction == SignalDirection.BUY
    assert context.entry_plan is not None
    assert context.stop_loss_plan is not None

    TakeProfitAnalyzer().analyze(context)

    assert context.take_profit_plan is not None

    # Entry = 100.5
    # SL = 98
    # Risk = 2.5
    # TP = 100.5 + (2.5 * 2) = 105.5
    assert context.take_profit_plan.take_profit == 105.5


def test_bearish_take_profit_uses_two_to_one_risk_reward():

    context = prepare_bearish_context()

    assert context.signal.direction == SignalDirection.SELL
    assert context.entry_plan is not None
    assert context.stop_loss_plan is not None

    TakeProfitAnalyzer().analyze(context)

    assert context.take_profit_plan is not None

    # Entry = 100.5
    # SL = 103
    # Risk = 2.5
    # TP = 100.5 - (2.5 * 2) = 95.5
    assert context.take_profit_plan.take_profit == 95.5


def test_no_take_profit_without_stop_loss():

    context = prepare_bullish_context()

    context.stop_loss_plan = None

    TakeProfitAnalyzer().analyze(context)

    assert context.take_profit_plan is None