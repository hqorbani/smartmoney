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

def test_runner_end_to_end_produces_trade_with_1r_and_2r_outcomes():
    df = make_ohlc_data(
        [
            # 0: bearish candle -> Bullish OB
            {
                "time": pd.Timestamp("2026-01-01 00:00:00"),
                "open": 95.0,
                "high": 100.0,
                "low": 90.0,
                "close": 92.0,
            },
            # 1: bullish impulse
            {
                "time": pd.Timestamp("2026-01-01 00:01:00"),
                "open": 92.0,
                "high": 110.0,
                "low": 101.0,
                "close": 108.0,
            },
            # 2: bullish FVG confirmation
            # low=102 > candle 0 high=100
            {
                "time": pd.Timestamp("2026-01-01 00:02:00"),
                "open": 108.0,
                "high": 109.0,
                "low": 102.0,
                "close": 106.0,
            },
            # 3: first touch of OB
            # Bullish OB = 90..100
            # low=98 => 20% penetration => FIRST
            {
                "time": pd.Timestamp("2026-01-01 00:03:00"),
                "open": 104.0,
                "high": 105.0,
                "low": 98.0,
                "close": 103.0,
            },
            # 4: reaches 1R from entry=98
            # risk = 98 - 90 = 8
            # 1R target = 106
            {
                "time": pd.Timestamp("2026-01-01 00:04:00"),
                "open": 103.0,
                "high": 106.0,
                "low": 101.0,
                "close": 105.0,
            },
            # 5: extra candle so outcome simulation has enough history
            {
                "time": pd.Timestamp("2026-01-01 00:05:00"),
                "open": 105.0,
                "high": 108.0,
                "low": 102.0,
                "close": 107.0,
            },
        ]
    )

    runner = HistoricalBacktestRunner(
        symbol="NAS100",
        timeframe=1,
    )

    results = runner.run(df)

    assert results

    trade = next(
        result
        for result in results
        if result.orderblock.index == 0
        and result.orderblock.bullish is True
    )

    assert trade.touch_index == 3
    assert trade.touch_zone is OrderBlockDepthZone.FIRST
    assert trade.penetration == pytest.approx(0.20)

    assert trade.entry_price == pytest.approx(98.0)

    assert trade.outcome_1r.entry_price == pytest.approx(98.0)
    assert trade.outcome_1r.stop_loss == pytest.approx(90.0)
    assert trade.outcome_1r.take_profit == pytest.approx(106.0)

    assert trade.outcome_2r.entry_price == pytest.approx(98.0)
    assert trade.outcome_2r.stop_loss == pytest.approx(90.0)
    assert trade.outcome_2r.take_profit == pytest.approx(114.0)

    assert trade.outcome_1r.outcome.value == "win"
    assert trade.outcome_1r.exit_index == 4

    assert trade.outcome_2r.outcome.value == "unresolved"        