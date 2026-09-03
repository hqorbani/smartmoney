import pandas as pd
import pytest

from smartmoney.backtesting.orderblock_zones import OrderBlockDepthZone
from smartmoney.backtesting.research import HistoricalResearchRunner


def make_ohlc_data(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)

    if "time" not in df.columns:
        df.insert(
            0,
            "time",
            pd.date_range(
                "2026-01-01",
                periods=len(df),
                freq="min",
            ),
        )

    return df


def test_research_runner_returns_result_for_dataframe():
    df = make_ohlc_data(
        [
            {
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
                "close": 100.0,
            },
        ]
    )

    runner = HistoricalResearchRunner(
        symbol="NAS100",
        timeframe=1,
    )

    result = runner.run(df)

    assert result.symbol == "NAS100"
    assert result.timeframe == 1
    assert result.candle_count == 1
    assert result.trades == []

    assert set(result.zone_stats) == {
        OrderBlockDepthZone.FIRST,
        OrderBlockDepthZone.MIDDLE,
        OrderBlockDepthZone.FINAL,
    }


def test_research_runner_uses_same_backtest_pipeline():
    df = make_ohlc_data(
        [
            {
                "open": 95.0,
                "high": 100.0,
                "low": 90.0,
                "close": 92.0,
            },
            {
                "open": 92.0,
                "high": 103.0,
                "low": 91.0,
                "close": 102.0,
            },
            {
                "open": 102.0,
                "high": 105.0,
                "low": 102.0,
                "close": 104.0,
            },
            {
                "open": 104.0,
                "high": 104.0,
                "low": 98.0,
                "close": 100.0,
            },
            {
                "open": 100.0,
                "high": 106.0,
                "low": 99.0,
                "close": 105.0,
            },
        ]
    )

    runner = HistoricalResearchRunner(
        symbol="NAS100",
        timeframe=1,
    )

    result = runner.run(df)

    assert result.trades

    trade = next(
        trade
        for trade in result.trades
        if trade.orderblock.index == 0
        and trade.orderblock.bullish is True
    )

    assert trade.touch_index == 3
    assert trade.touch_zone is OrderBlockDepthZone.FIRST

    first_stats = result.zone_stats[OrderBlockDepthZone.FIRST]

    assert first_stats.touches >= 1
    assert first_stats.zone_frequency > 0.0


def test_research_runner_rejects_invalid_candle_count():
    runner = HistoricalResearchRunner(
        symbol="NAS100",
        timeframe=1,
    )

    class DummyProvider:
        pass

    with pytest.raises(ValueError, match="candle_count"):
        runner.run_from_provider(
            provider=DummyProvider(),
            candle_count=0,
        )


def test_run_from_provider_uses_closed_candles_only():
    class FakeProvider:
        def __init__(self):
            self.connected = False
            self.shutdown_called = False
            self.requested_count = None

        def connect(self):
            self.connected = True

        def shutdown(self):
            self.shutdown_called = True
            self.connected = False

        def fetch_rates(self, symbol, timeframe, count):
            self.requested_count = count

            return make_ohlc_data(
                [
                    {
                        "open": 100.0,
                        "high": 101.0,
                        "low": 99.0,
                        "close": 100.0,
                    },
                    {
                        "open": 100.0,
                        "high": 102.0,
                        "low": 99.0,
                        "close": 101.0,
                    },
                    {
                        "open": 101.0,
                        "high": 103.0,
                        "low": 100.0,
                        "close": 102.0,
                    },
                    {
                        "open": 102.0,
                        "high": 104.0,
                        "low": 101.0,
                        "close": 103.0,
                    },
                ]
            )

    provider = FakeProvider()

    runner = HistoricalResearchRunner(
        symbol="NAS100",
        timeframe=1,
    )

    result = runner.run_from_provider(
        provider=provider,
        candle_count=3,
    )

    assert provider.requested_count == 4
    assert provider.shutdown_called is True
    assert result.candle_count == 3


def test_run_from_provider_shuts_down_provider_when_fetch_fails():
    class FailingProvider:
        def __init__(self):
            self.shutdown_called = False

        def connect(self):
            pass

        def shutdown(self):
            self.shutdown_called = True

        def fetch_rates(self, symbol, timeframe, count):
            raise RuntimeError("MT5 fetch failed")

    provider = FailingProvider()

    runner = HistoricalResearchRunner(
        symbol="NAS100",
        timeframe=1,
    )

    with pytest.raises(RuntimeError, match="MT5 fetch failed"):
        runner.run_from_provider(
            provider=provider,
            candle_count=100,
        )

    assert provider.shutdown_called is True