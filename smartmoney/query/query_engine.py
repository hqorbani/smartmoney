from __future__ import annotations

from smartmoney.models.signal import Signal


class QueryEngine:

    def query(
        self,
        signals: list[Signal],
        *,
        symbol: str | None = None,
        timeframe: int | None = None,
        minimum_score: float | None = None,
        sort_by: str = "score",
        descending: bool = True,
        limit: int | None = None,
    ) -> list[Signal]:

        result = list(signals)

        # -----------------------------------------
        # Filters
        # -----------------------------------------

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

        if minimum_score is not None:

            result = [
                s
                for s in result
                if s.score >= minimum_score
            ]

        # -----------------------------------------
        # Sorting
        # -----------------------------------------

        key_functions = {

            "score":
                lambda s: s.score,

            "time":
                lambda s: s.time,

            "price":
                lambda s: s.price,

        }

        key = key_functions.get(
            sort_by,
            key_functions["score"],
        )

        result.sort(
            key=key,
            reverse=descending,
        )

        # -----------------------------------------
        # Limit
        # -----------------------------------------

        if limit is not None:

            result = result[:limit]

        return result