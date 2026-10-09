import pandas as pd
import pytest

from smartmoney.analyzers.entry import EntryAnalyzer
from smartmoney.analyzers.fvg import FVGAnalyzer
from smartmoney.analyzers.orderblock import OrderBlockAnalyzer
from smartmoney.analyzers.signal import SignalAnalyzer
from smartmoney.analyzers.stoploss import StopLossAnalyzer
from smartmoney.core.context import MarketContext
from smartmoney.models.entry import EntryPlan, EntryZone
from smartmoney.models.signal import SignalDirection
from smartmoney.services.atr_service import ATRService


def make_context(rows):
    df = pd.DataFrame(rows)
    df["time"] = pd.to_datetime(df["time"])

    return MarketContext(
        symbol="XAUUSD",
        timeframe=15,
        df=df,
    )


def mock_atr(self, df, period):
    """Return deterministic ATR values for tests."""
    return pd.Series(4.0, index=df.index, dtype=float)


def prepare_bullish_context(monkeypatch):
    monkeypatch.setattr(ATRService, "calculate", mock_atr)

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

    # Adjust the last candle to create the intended entry setup.
    context.df.loc[2, "high"] = 102
    context.df.loc[2, "low"] = 99
    context.df.loc[2, "close"] = 100

    EntryAnalyzer().analyze(context)
    StopLossAnalyzer().analyze(context)

    return context


def prepare_bearish_context(monkeypatch):
    monkeypatch.setattr(ATRService, "calculate", mock_atr)

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

    # Adjust the last candle to create the intended entry setup.
    context.df.loc[2, "high"] = 102
    context.df.loc[2, "low"] = 99
    context.df.loc[2, "close"] = 101

    EntryAnalyzer().analyze(context)
    StopLossAnalyzer().analyze(context)

    return context


def test_bullish_stop_loss_is_orderblock_low(monkeypatch):
    context = prepare_bullish_context(monkeypatch)

    assert context.signal.direction == SignalDirection.BUY
    assert context.entry_plan is not None
    assert context.stop_loss_plan is not None

    expected_stop = float(context.entry_plan.orderblock.expanded_low)

    assert context.stop_loss_plan.stop_loss == pytest.approx(
        expected_stop
    )


def test_bearish_stop_loss_is_orderblock_high(monkeypatch):
    context = prepare_bearish_context(monkeypatch)

    assert context.signal.direction == SignalDirection.SELL
    assert context.entry_plan is not None
    assert context.stop_loss_plan is not None

    expected_stop = float(context.entry_plan.orderblock.expanded_high)

    assert context.stop_loss_plan.stop_loss == pytest.approx(
        expected_stop
    )


def test_no_stop_loss_without_entry_plan():
    context = make_context([
        {
            "time": "2026-01-01 10:00",
            "open": 100,
            "high": 105,
            "low": 95,
            "close": 101,
        },
    ])

    context.entry_plan = None

    StopLossAnalyzer().analyze(context)

    assert context.stop_loss_plan is None


def test_no_stop_loss_when_bullish_stop_is_not_below_entry(monkeypatch):
    context = prepare_bullish_context(monkeypatch)

    assert context.entry_plan is not None

    entry_price = float(context.entry_plan.entry_price)

    # Force the expanded lower boundary to be at or above entry.
    context.entry_plan.orderblock.expanded_low = entry_price

    StopLossAnalyzer().analyze(context)

    assert context.stop_loss_plan is None


def test_no_stop_loss_when_bearish_stop_is_not_above_entry(monkeypatch):
    context = prepare_bearish_context(monkeypatch)

    assert context.entry_plan is not None

    entry_price = float(context.entry_plan.entry_price)

    # Force the expanded upper boundary to be at or below entry.
    context.entry_plan.orderblock.expanded_high = entry_price

    StopLossAnalyzer().analyze(context)

    assert context.stop_loss_plan is None


def test_no_stop_loss_when_expanded_boundary_is_missing(monkeypatch):
    context = prepare_bullish_context(monkeypatch)

    assert context.entry_plan is not None

    context.entry_plan.orderblock.expanded_low = None

    StopLossAnalyzer().analyze(context)

    assert context.stop_loss_plan is None
