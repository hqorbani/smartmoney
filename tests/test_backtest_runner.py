import pandas as pd
import pytest

from smartmoney.backtesting.runner import HistoricalBacktestRunner
from smartmoney.backtesting.orderblock_zones import OrderBlockDepthZone


def make_ohlc_data(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows)


def test_runner_returns_empty_result_for_empty_dataframe():
    runner = HistoricalBacktestRunner(
        symbol="NAS100",
        timeframe=1,
    )

    result = runner.run(pd.DataFrame())

    assert result == []


def test_runner_rejects_dataframe_without_required_columns():
    runner = HistoricalBacktestRunner(
        symbol="NAS100",
        timeframe=1,
    )

    df = pd.DataFrame(
        [
            {
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
            }
        ]
    )

    with pytest.raises(ValueError):
        runner.run(df)


def test_runner_does_not_create_touch_before_ob_confirmation():
    df = make_ohlc_data(
        [
            {
                "time": pd.Timestamp("2026-01-01 00:00:00"),
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
                "close": 100.0,
            },
            {
                "time": pd.Timestamp("2026-01-01 00:01:00"),
                "open": 100.0,
                "high": 102.0,
                "low": 100.0,
                "close": 101.0,
            },
            {
                "time": pd.Timestamp("2026-01-01 00:02:00"),
                "open": 101.0,
                "high": 105.0,
                "low": 103.0,
                "close": 104.0,
            },
        ]
    )

    runner = HistoricalBacktestRunner(
        symbol="NAS100",
        timeframe=1,
    )

    results = runner.run(df)

    for result in results:
        assert result.touch_index > result.orderblock.related_fvg.end_index


def test_runner_result_contains_touch_information():
    df = make_ohlc_data(
        [
            {
                "time": pd.Timestamp("2026-01-01 00:00:00"),
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
                "close": 100.0,
            },
            {
                "time": pd.Timestamp("2026-01-01 00:01:00"),
                "open": 100.0,
                "high": 102.0,
                "low": 100.0,
                "close": 101.0,
            },
            {
                "time": pd.Timestamp("2026-01-01 00:02:00"),
                "open": 101.0,
                "high": 105.0,
                "low": 103.0,
                "close": 104.0,
            },
        ]
    )

    runner = HistoricalBacktestRunner(
        symbol="NAS100",
        timeframe=1,
    )

    results = runner.run(df)

    for result in results:
        assert isinstance(result.touch_index, int)
        assert isinstance(result.touch_zone, OrderBlockDepthZone)
        assert 0.0 <= result.penetration <= 1.0


def test_runner_uses_forward_only_context():
    df = make_ohlc_data(
        [
            {
                "time": pd.Timestamp("2026-01-01 00:00:00"),
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
                "close": 100.0,
            },
            {
                "time": pd.Timestamp("2026-01-01 00:01:00"),
                "open": 100.0,
                "high": 102.0,
                "low": 100.0,
                "close": 101.0,
            },
            {
                "time": pd.Timestamp("2026-01-01 00:02:00"),
                "open": 101.0,
                "high": 105.0,
                "low": 103.0,
                "close": 104.0,
            },
        ]
    )

    runner = HistoricalBacktestRunner(
        symbol="NAS100",
        timeframe=1,
    )

    results = runner.run(df)

    for result in results:
        assert result.orderblock.index < result.touch_index
        assert result.touch_index < len(df)