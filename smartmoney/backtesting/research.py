from dataclasses import dataclass

import pandas as pd

from smartmoney.backtesting.orderblock_stats import (
    OrderBlockZoneStats,
    analyze_orderblock_zones,
)
from smartmoney.backtesting.orderblock_zones import OrderBlockDepthZone
from smartmoney.backtesting.runner import (
    BacktestTrade,
    HistoricalBacktestRunner,
)
from smartmoney.core.mt5 import MT5DataProvider

@dataclass(frozen=True, slots=True)
class HistoricalResearchResult:
    symbol: str
    timeframe: int
    candle_count: int
    trades: list[BacktestTrade]
    zone_stats: dict[OrderBlockDepthZone, OrderBlockZoneStats]


class HistoricalResearchRunner:
    """
    Execute the Order Block zone research on historical OHLC data.

    The dataframe path is deterministic and does not require MT5.
    The provider path fetches closed candles from MT5 and then delegates
    to the same dataframe execution path.
    """

    def __init__(self, symbol: str, timeframe: int) -> None:
        self.symbol = symbol
        self.timeframe = timeframe
        self._backtest_runner = HistoricalBacktestRunner(
            symbol=symbol,
            timeframe=timeframe,
        )

    def run(self, df: pd.DataFrame) -> HistoricalResearchResult:
        """
        Run the research on an already prepared historical dataframe.
        """
        trades = self._backtest_runner.run(df)
        zone_stats = analyze_orderblock_zones(trades)

        return HistoricalResearchResult(
            symbol=self.symbol,
            timeframe=self.timeframe,
            candle_count=len(df),
            trades=trades,
            zone_stats=zone_stats,
        )

    def run_from_provider(
        self,
        provider: MT5DataProvider,
        candle_count: int,
    ) -> HistoricalResearchResult:
        """
        Fetch closed historical candles from MT5 and run the research.

        `fetch_rates()` includes the current candle because it starts at
        position 0. We therefore request one extra candle and discard the
        final row before running the backtest.
        """
        if candle_count <= 0:
            raise ValueError("candle_count must be greater than zero")

        provider.connect()

        try:
            df = provider.fetch_rates(
                symbol=self.symbol,
                timeframe=self.timeframe,
                count=candle_count + 1,
            )
        finally:
            provider.shutdown()

        if df.empty:
            return self.run(df)

        if len(df) == 1:
            return self.run(df.iloc[:0].copy())

        closed_df = df.iloc[:-1].copy()

        return self.run(closed_df)