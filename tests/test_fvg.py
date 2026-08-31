import pandas as pd

from smartmoney.analyzers.fvg import FVGAnalyzer
from smartmoney.analyzers.fvg_lifecycle import FVGLifecycleAnalyzer
from smartmoney.core.context import MarketContext
from smartmoney.models.fvg import FVGStatus


def make_context(rows):
    df = pd.DataFrame(rows)
    df["time"] = pd.to_datetime(df["time"])

    return MarketContext(
        symbol="TEST",
        timeframe=15,
        df=df,
    )


def test_bullish_fvg_is_detected():
    context = make_context([
        {"time": "2026-01-01 10:00", "high": 100, "low": 98},
        {"time": "2026-01-01 10:15", "high": 105, "low": 99},
        {"time": "2026-01-01 10:30", "high": 108, "low": 102},
    ])

    FVGAnalyzer().analyze(context)

    assert len(context.fvgs) == 1

    fvg = context.fvgs[0]

    assert fvg.bullish is True
    assert fvg.low == 100
    assert fvg.high == 102
    assert fvg.status == FVGStatus.ACTIVE


def test_bearish_fvg_is_detected():
    context = make_context([
        {"time": "2026-01-01 10:00", "high": 102, "low": 100},
        {"time": "2026-01-01 10:15", "high": 101, "low": 95},
        {"time": "2026-01-01 10:30", "high": 98, "low": 92},
        {"time": "2026-01-01 10:45", "high": 96, "low": 90},
    ])

    FVGAnalyzer().analyze(context)

    assert len(context.fvgs) == 1

    fvg = context.fvgs[0]

    assert fvg.bullish is False
    assert fvg.low == 98
    assert fvg.high == 100
    assert fvg.status == FVGStatus.ACTIVE


def test_bullish_fvg_becomes_mitigated():
    context = make_context([
        {"time": "2026-01-01 10:00", "high": 100, "low": 98},
        {"time": "2026-01-01 10:15", "high": 105, "low": 99},
        {"time": "2026-01-01 10:30", "high": 108, "low": 102},
        {"time": "2026-01-01 10:45", "high": 106, "low": 101},
    ])

    FVGAnalyzer().analyze(context)
    FVGLifecycleAnalyzer().analyze(context)

    fvg = context.fvgs[0]

    assert fvg.status == FVGStatus.MITIGATED
    assert fvg.mitigation_time == pd.Timestamp("2026-01-01 10:45")


def test_bullish_fvg_becomes_filled():
    context = make_context([
        {"time": "2026-01-01 10:00", "high": 100, "low": 98},
        {"time": "2026-01-01 10:15", "high": 105, "low": 99},
        {"time": "2026-01-01 10:30", "high": 108, "low": 102},
        {"time": "2026-01-01 10:45", "high": 106, "low": 99},
    ])

    FVGAnalyzer().analyze(context)
    FVGLifecycleAnalyzer().analyze(context)

    assert context.fvgs[0].status == FVGStatus.FILLED


def test_existing_fvg_is_not_duplicated():
    context = make_context([
        {"time": "2026-01-01 10:00", "high": 100, "low": 98},
        {"time": "2026-01-01 10:15", "high": 105, "low": 99},
        {"time": "2026-01-01 10:30", "high": 108, "low": 102},
    ])

    analyzer = FVGAnalyzer()

    analyzer.analyze(context)
    analyzer.analyze(context)

    assert len(context.fvgs) == 1


def test_fvg_state_is_preserved_across_analysis_cycles():
    context = make_context([
        {"time": "2026-01-01 10:00", "high": 100, "low": 98},
        {"time": "2026-01-01 10:15", "high": 105, "low": 99},
        {"time": "2026-01-01 10:30", "high": 108, "low": 102},
        {"time": "2026-01-01 10:45", "high": 106, "low": 101},
    ])

    FVGAnalyzer().analyze(context)
    FVGLifecycleAnalyzer().analyze(context)

    assert context.fvgs[0].status == FVGStatus.MITIGATED

    fvg_before = context.fvgs[0]

    FVGAnalyzer().analyze(context)
    FVGLifecycleAnalyzer().analyze(context)

    assert len(context.fvgs) == 1
    assert context.fvgs[0] is fvg_before
    assert context.fvgs[0].status == FVGStatus.MITIGATED

def test_fvg_state_is_preserved_when_new_candle_arrives():
    context = make_context([
        {"time": "2026-01-01 10:00", "high": 100, "low": 98},
        {"time": "2026-01-01 10:15", "high": 105, "low": 99},
        {"time": "2026-01-01 10:30", "high": 108, "low": 102},
        {"time": "2026-01-01 10:45", "high": 106, "low": 101},
    ])

    FVGAnalyzer().analyze(context)
    FVGLifecycleAnalyzer().analyze(context)

    fvg_before = context.fvgs[0]

    assert fvg_before.status == FVGStatus.MITIGATED

    context.df = pd.DataFrame([
        {"time": "2026-01-01 10:00", "high": 100, "low": 98},
        {"time": "2026-01-01 10:15", "high": 105, "low": 99},
        {"time": "2026-01-01 10:30", "high": 108, "low": 102},
        {"time": "2026-01-01 10:45", "high": 106, "low": 101},
        {"time": "2026-01-01 11:00", "high": 109, "low": 105},
    ])

    context.df["time"] = pd.to_datetime(context.df["time"])

    FVGAnalyzer().analyze(context)
    FVGLifecycleAnalyzer().analyze(context)

    assert context.fvgs[0] is fvg_before
    assert context.fvgs[0].status == FVGStatus.MITIGATED

def test_mitigated_fvg_becomes_filled_when_new_candle_fills_gap():
    context = make_context([
        {"time": "2026-01-01 10:00", "high": 100, "low": 98},
        {"time": "2026-01-01 10:15", "high": 105, "low": 99},
        {"time": "2026-01-01 10:30", "high": 108, "low": 102},
        {"time": "2026-01-01 10:45", "high": 106, "low": 101},
    ])

    FVGAnalyzer().analyze(context)
    FVGLifecycleAnalyzer().analyze(context)

    fvg_before = context.fvgs[0]

    assert fvg_before.status == FVGStatus.MITIGATED

    context.df = pd.DataFrame([
        {"time": "2026-01-01 10:00", "high": 100, "low": 98},
        {"time": "2026-01-01 10:15", "high": 105, "low": 99},
        {"time": "2026-01-01 10:30", "high": 108, "low": 102},
        {"time": "2026-01-01 10:45", "high": 106, "low": 101},
        {"time": "2026-01-01 11:00", "high": 104, "low": 99},
    ])

    context.df["time"] = pd.to_datetime(context.df["time"])

    FVGAnalyzer().analyze(context)
    FVGLifecycleAnalyzer().analyze(context)

    assert context.fvgs[0] is fvg_before
    assert context.fvgs[0].status == FVGStatus.FILLED