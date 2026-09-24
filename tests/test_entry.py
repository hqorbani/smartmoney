import pandas as pd

from smartmoney.analyzers.entry import EntryAnalyzer
from smartmoney.analyzers.fvg import FVGAnalyzer
from smartmoney.analyzers.orderblock import OrderBlockAnalyzer
from smartmoney.analyzers.signal import SignalAnalyzer
from smartmoney.core.context import MarketContext
from smartmoney.models.signal import SignalDirection


def make_context(rows):
    df = pd.DataFrame(rows)
    df["time"] = pd.to_datetime(df["time"])

    return MarketContext(
        symbol="EURUSD",
        timeframe=15,
        df=df,
    )
def test_bullish_entry_is_created_when_price_is_inside_orderblock():

    rows = []

    for i in range(10):
        rows.append({
            "time": f"2026-01-01 {10 + i // 4:02d}:{(i % 4) * 15:02d}",
            "open": 100,
            "high": 101,
            "low": 99,
            "close": 100,
        })

    rows.extend([
        {
            "time": "2026-01-01 12:30",
            "open": 101,
            "high": 103,
            "low": 98,
            "close": 99,
        },
        {
            "time": "2026-01-01 12:45",
            "open": 99,
            "high": 108,
            "low": 99,
            "close": 107,
        },
        {
            "time": "2026-01-01 13:00",
            "open": 107,
            "high": 112,
            "low": 105,
            "close": 110,
        },
    ])

    context = make_context(rows)

    FVGAnalyzer().analyze(context)
    OrderBlockAnalyzer().analyze(context)
    SignalAnalyzer().analyze(context)

    assert context.signal.direction == SignalDirection.BUY

    # Simulate price returning to the OB
    context.df.loc[12, "high"] = 102
    context.df.loc[12, "low"] = 99
    context.df.loc[12, "close"] = 100

    EntryAnalyzer().analyze(context)

    assert context.entry_plan is not None
    assert context.entry_plan.entry_price == 100.5
    assert context.entry_plan.orderblock is context.orderblocks[0]
    assert context.entry_plan.fvg is context.fvgs[0]

def test_bearish_entry_is_created_when_price_is_inside_orderblock():

    rows = []

    for i in range(10):
        rows.append({
            "time": f"2026-01-01 {10 + i // 4:02d}:{(i % 4) * 15:02d}",
            "open": 100,
            "high": 101,
            "low": 99,
            "close": 100,
        })

    rows.extend([
        {
            "time": "2026-01-01 12:30",
            "open": 99,
            "high": 103,
            "low": 98,
            "close": 102,
        },
        {
            "time": "2026-01-01 12:45",
            "open": 102,
            "high": 102,
            "low": 93,
            "close": 94,
        },
        {
            "time": "2026-01-01 13:00",
            "open": 94,
            "high": 96,
            "low": 90,
            "close": 91,
        },
    ])

    context = make_context(rows)

    FVGAnalyzer().analyze(context)
    OrderBlockAnalyzer().analyze(context)
    SignalAnalyzer().analyze(context)

    assert context.signal.direction == SignalDirection.SELL

    # Simulate price returning to the OB
    context.df.loc[12, "high"] = 102
    context.df.loc[12, "low"] = 99
    context.df.loc[12, "close"] = 101
    EntryAnalyzer().analyze(context)

    assert context.entry_plan is not None
    assert context.entry_plan.entry_price == 100.5
    assert context.entry_plan.orderblock is context.orderblocks[0]
    assert context.entry_plan.fvg is context.fvgs[0]    

def test_no_entry_plan_without_signal():

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
    EntryAnalyzer().analyze(context)

    assert context.entry_plan is None

def test_no_entry_plan_when_price_is_outside_bullish_orderblock():

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
        {
            "time": "2026-01-01 10:45",
            "open": 110,
            "high": 115,
            "low": 109,
            "close": 113,
        },
    ])

    FVGAnalyzer().analyze(context)
    OrderBlockAnalyzer().analyze(context)
    SignalAnalyzer().analyze(context)
    EntryAnalyzer().analyze(context)

    assert context.signal.direction == SignalDirection.BUY
    assert context.entry_plan is None


def test_no_entry_plan_when_price_is_outside_bearish_orderblock():

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
        {
            "time": "2026-01-01 10:45",
            "open": 91,
            "high": 95,
            "low": 90,
            "close": 94,
        },
    ])

    FVGAnalyzer().analyze(context)
    OrderBlockAnalyzer().analyze(context)
    SignalAnalyzer().analyze(context)
    EntryAnalyzer().analyze(context)

    assert context.signal.direction == SignalDirection.SELL
    assert context.entry_plan is None

def test_bullish_entry_zones_are_split_into_three_equal_parts():

    rows = []

    for i in range(10):
        rows.append({
            "time": f"2026-01-01 {10 + i // 4:02d}:{(i % 4) * 15:02d}",
            "open": 100,
            "high": 101,
            "low": 99,
            "close": 100,
        })

    rows.extend([
        {
            "time": "2026-01-01 12:30",
            "open": 101,
            "high": 103,
            "low": 98,
            "close": 99,
        },
        {
            "time": "2026-01-01 12:45",
            "open": 99,
            "high": 108,
            "low": 99,
            "close": 107,
        },
        {
            "time": "2026-01-01 13:00",
            "open": 107,
            "high": 112,
            "low": 105,
            "close": 110,
        },
    ])

    context = make_context(rows)

    FVGAnalyzer().analyze(context)
    OrderBlockAnalyzer().analyze(context)
    SignalAnalyzer().analyze(context)
    EntryAnalyzer().analyze(context)

    zones = context.entry_plan.zones

    assert [zone.name for zone in zones] == [
        "INITIAL",
        "MIDDLE",
        "FINAL",
    ]

    ob = context.orderblocks[0]

    low = ob.expanded_low
    high = ob.expanded_high
    zone_size = (high - low) / 3.0

    assert zones[0].price_low == low
    assert zones[0].price_high == low + zone_size

    assert zones[1].price_low == low + zone_size
    assert zones[1].price_high == low + (zone_size * 2)

    assert zones[2].price_low == low + (zone_size * 2)
    assert zones[2].price_high == high

def test_bearish_entry_zones_follow_price_direction():

    rows = []

    for i in range(10):
        rows.append({
            "time": f"2026-01-01 {10 + i // 4:02d}:{(i % 4) * 15:02d}",
            "open": 100,
            "high": 101,
            "low": 99,
            "close": 100,
        })

    rows.extend([
        {
            "time": "2026-01-01 12:30",
            "open": 99,
            "high": 103,
            "low": 98,
            "close": 102,
        },
        {
            "time": "2026-01-01 12:45",
            "open": 102,
            "high": 102,
            "low": 93,
            "close": 94,
        },
        {
            "time": "2026-01-01 13:00",
            "open": 94,
            "high": 96,
            "low": 90,
            "close": 91,
        },
    ])

    context = make_context(rows)

    FVGAnalyzer().analyze(context)
    OrderBlockAnalyzer().analyze(context)
    SignalAnalyzer().analyze(context)
    EntryAnalyzer().analyze(context)

    zones = context.entry_plan.zones

    assert [zone.name for zone in zones] == [
        "INITIAL",
        "MIDDLE",
        "FINAL",
    ]

    ob = context.orderblocks[0]

    low = ob.expanded_low
    high = ob.expanded_high
    zone_size = (high - low) / 3.0

    assert zones[0].price_low == high - zone_size
    assert zones[0].price_high == high

    assert zones[1].price_low == high - (zone_size * 2)
    assert zones[1].price_high == high - zone_size

    assert zones[2].price_low == low
    assert zones[2].price_high == high - (zone_size * 2)    