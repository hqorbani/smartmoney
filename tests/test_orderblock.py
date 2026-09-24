import pandas as pd

from smartmoney.analyzers.fvg import FVGAnalyzer
from smartmoney.analyzers.orderblock import OrderBlockAnalyzer
from smartmoney.core.context import MarketContext


def make_context(rows):
    df = pd.DataFrame(rows)
    df["time"] = pd.to_datetime(df["time"])

    return MarketContext(
        symbol="EURUSD",
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

def test_orderblock_is_preserved_across_analysis_cycles():
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

    assert len(context.orderblocks) == 1

    ob_before = context.orderblocks[0]

    context.df = pd.DataFrame([
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
            "low": 108,
            "close": 113,
        },
    ])

    context.df["time"] = pd.to_datetime(context.df["time"])

    FVGAnalyzer().analyze(context)
    OrderBlockAnalyzer().analyze(context)

    assert len(context.orderblocks) == 1
    assert context.orderblocks[0] is ob_before  

def test_orderblock_state_is_preserved_across_analysis_cycles():
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

    ob_before = context.orderblocks[0]

    ob_before.mitigated = True

    context.df = pd.DataFrame([
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
            "low": 108,
            "close": 113,
        },
    ])

    context.df["time"] = pd.to_datetime(context.df["time"])

    FVGAnalyzer().analyze(context)
    OrderBlockAnalyzer().analyze(context)

    assert len(context.orderblocks) == 1
    assert context.orderblocks[0] is ob_before
    assert context.orderblocks[0].mitigated is True  

def test_bullish_orderblock_is_mitigated_when_price_enters_zone():
    context = make_context([
        # Bullish OB candle
        {
            "time": "2026-01-01 10:00",
            "open": 101,
            "high": 103,
            "low": 98,
            "close": 99,
        },
        # Impulse candle
        {
            "time": "2026-01-01 10:15",
            "open": 99,
            "high": 108,
            "low": 99,
            "close": 107,
        },
        # FVG candle
        {
            "time": "2026-01-01 10:30",
            "open": 107,
            "high": 112,
            "low": 105,
            "close": 110,
        },
        # Price returns into OB zone
        {
            "time": "2026-01-01 10:45",
            "open": 110,
            "high": 111,
            "low": 102,
            "close": 105,
        },
        # Current candle
        {
            "time": "2026-01-01 11:00",
            "open": 105,
            "high": 106,
            "low": 104,
            "close": 105,
        },
    ])

    FVGAnalyzer().analyze(context)
    OrderBlockAnalyzer().analyze(context)

    assert len(context.orderblocks) == 1

    ob = context.orderblocks[0]

    assert ob.bullish is True
    assert ob.mitigated is True    
    assert ob.mitigation_index == 3
    assert ob.mitigation_time == pd.Timestamp("2026-01-01 10:45")    

def test_bearish_orderblock_is_mitigated_when_price_enters_zone():
    context = make_context([
        # Bearish OB candle
        {
            "time": "2026-01-01 10:00",
            "open": 99,
            "high": 103,
            "low": 98,
            "close": 102,
        },
        # Impulse candle
        {
            "time": "2026-01-01 10:15",
            "open": 102,
            "high": 102,
            "low": 93,
            "close": 94,
        },
        # FVG candle
        {
            "time": "2026-01-01 10:30",
            "open": 94,
            "high": 96,
            "low": 90,
            "close": 91,
        },
        # Price returns into OB zone
        {
            "time": "2026-01-01 10:45",
            "open": 91,
            "high": 100,
            "low": 89,
            "close": 98,
        },
        # Current candle
        {
            "time": "2026-01-01 11:00",
            "open": 98,
            "high": 99,
            "low": 96,
            "close": 97,
        },
    ])

    FVGAnalyzer().analyze(context)
    OrderBlockAnalyzer().analyze(context)

    assert len(context.orderblocks) == 1

    ob = context.orderblocks[0]

    assert ob.bullish is False
    assert ob.mitigated is True    
    assert ob.mitigation_index == 3
    assert ob.mitigation_time == pd.Timestamp("2026-01-01 10:45")

def test_orderblock_atr_uses_exact_orderblock_candle():
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

    ob = context.orderblocks[0]

    assert ob.index == 0

def test_orderblock_without_valid_atr_remains_unchanged():
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

    ob = context.orderblocks[0]

    assert ob.index == 0
    assert ob.low == 98
    assert ob.high == 103        