from __future__ import annotations

from collections.abc import Iterable

from smartmoney.models.signal import Signal


class QueryEngine:

    def query(
        self,
        signals: Iterable[Signal],
        *,
        symbol: str | None = None,
        timeframe: int | None = None,
        strategy: str | None = None,
        direction: str | None = None,
        minimum_score: float | None = None,
        sort_by: str = "score",
        descending: bool = True,
        limit: int | None = None,
    ) -> list[Signal]:

        result = list(signals)

        # --------------------------------------------------
        # Filters
        # --------------------------------------------------

        if symbol is not None:

            result = [
                s
                for s in result
                if s.symbol == symbol
            ]

        if timeframe is not None:

            result = [
                s
                for s in result
                if s.timeframe == timeframe
            ]

        if strategy is not None:

            result = [
                s
                for s in result
                if s.strategy == strategy
            ]

        if direction is not None:

            result = [
                s
                for s in result
                if s.direction == direction
            ]

        if minimum_score is not None:

            result = [
                s
                for s in result
                if s.score >= minimum_score
            ]

        # --------------------------------------------------
        # Sorting
        # --------------------------------------------------

        sort_keys = {

            "score":
                lambda s: s.score,

            "distance":
                lambda s: s.distance,

            "time":
                lambda s: s.time,

            "symbol":
                lambda s: s.symbol,

            "strategy":
                lambda s: s.strategy,

            "direction":
                lambda s: s.direction,

            "price_low":
                lambda s: s.price_low,

            "price_high":
                lambda s: s.price_high,
        }

        key = sort_keys.get(
            sort_by,
            sort_keys["score"],
        )

        result.sort(
            key=key,
            reverse=descending,
        )

        # --------------------------------------------------
        # Limit
        # --------------------------------------------------

        if limit is not None:

            result = result[:limit]

        return result