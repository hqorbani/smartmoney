from dataclasses import dataclass

import pandas as pd

from smartmoney.analyzers.fvg import FVGAnalyzer
from smartmoney.analyzers.orderblock import OrderBlockAnalyzer
from smartmoney.backtesting.orderblock_zones import (
    OrderBlockDepthZone,
)
from smartmoney.core.context import MarketContext
from smartmoney.models.orderblock import OrderBlock


@dataclass(frozen=True, slots=True)
class BacktestOrderBlock:
    orderblock: OrderBlock
    touch_index: int
    touch_zone: OrderBlockDepthZone
    penetration: float


class HistoricalBacktestRunner:
    """
    Replays historical candles without exposing future candles
    to the analyzers or to the first-touch calculation.
    """

    def __init__(
        self,
        symbol: str,
        timeframe: int,
    ) -> None:
        self.symbol = symbol
        self.timeframe = timeframe

        self._fvg_analyzer = FVGAnalyzer()
        self._orderblock_analyzer = OrderBlockAnalyzer()

    def run(self, df: pd.DataFrame) -> list[BacktestOrderBlock]:
        if df.empty:
            return []

        self._validate_dataframe(df)

        context = MarketContext(
            symbol=self.symbol,
            timeframe=self.timeframe,
            df=df.iloc[:0].copy(),
        )

        known_orderblocks: set[tuple[int, bool]] = set()
        pending_orderblocks: list[OrderBlock] = []
        results: list[BacktestOrderBlock] = []

        for current_index in range(len(df)):
            context.df = df.iloc[: current_index + 1].copy()

            self._fvg_analyzer.analyze(context)
            self._orderblock_analyzer.analyze(context)

            self._register_confirmed_orderblocks(
                context.orderblocks,
                current_index,
                known_orderblocks,
                pending_orderblocks,
            )

            remaining: list[OrderBlock] = []

            for ob in pending_orderblocks:
                touch = self._check_touch(
                    df.iloc[current_index],
                    ob,
                )

                if touch is None:
                    remaining.append(ob)
                    continue

                results.append(
                    BacktestOrderBlock(
                        orderblock=ob,
                        touch_index=current_index,
                        touch_zone=touch[0],
                        penetration=touch[1],
                    )
                )

            pending_orderblocks = remaining

        return results

    @staticmethod
    def _register_confirmed_orderblocks(
        orderblocks: list[OrderBlock],
        current_index: int,
        known_orderblocks: set[tuple[int, bool]],
        pending_orderblocks: list[OrderBlock],
    ) -> None:
        for ob in orderblocks:
            key = (ob.index, ob.bullish)

            if key in known_orderblocks:
                continue

            if ob.related_fvg is None:
                continue

            confirmation_index = ob.related_fvg.end_index

            if confirmation_index >= current_index:
                continue

            known_orderblocks.add(key)
            pending_orderblocks.append(ob)

    @staticmethod
    def _check_touch(
        candle: pd.Series,
        ob: OrderBlock,
    ) -> tuple[OrderBlockDepthZone, float] | None:
        if candle["low"] > ob.high or candle["high"] < ob.low:
            return None

        depth = ob.high - ob.low

        if depth <= 0:
            raise ValueError("Order Block high must be greater than low")

        if ob.bullish:
            penetration = (ob.high - float(candle["low"])) / depth
        else:
            penetration = (float(candle["high"]) - ob.low) / depth

        penetration = min(1.0, max(0.0, penetration))

        if penetration <= 1.0 / 3.0:
            zone = OrderBlockDepthZone.FIRST
        elif penetration <= 2.0 / 3.0:
            zone = OrderBlockDepthZone.MIDDLE
        else:
            zone = OrderBlockDepthZone.FINAL

        return zone, penetration

    @staticmethod
    def _validate_dataframe(df: pd.DataFrame) -> None:
        required_columns = {"open", "high", "low", "close"}

        missing = required_columns.difference(df.columns)

        if missing:
            raise ValueError(
                f"DataFrame is missing required columns: {sorted(missing)}"
            )