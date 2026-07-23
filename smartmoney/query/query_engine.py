from __future__ import annotations

from collections.abc import Iterable

from smartmoney.models.signal import Signal
from smartmoney.query.query import Query


class QueryEngine:

    def query(
        self,
        signals: Iterable[Signal],
        query: Query,
    ) -> list[Signal]:

        result = list(signals)

        # ----------------------------------------
        # Filters
        # ----------------------------------------

        if query.symbol is not None:

            result = [
                signal
                for signal in result
                if signal.symbol == query.symbol
            ]

        if query.timeframe is not None:

            result = [
                signal
                for signal in result
                if signal.timeframe == query.timeframe
            ]

        if query.strategy is not None:

            result = [
                signal
                for signal in result
                if signal.strategy == query.strategy
            ]

        if query.direction is not None:

            result = [
                signal
                for signal in result
                if signal.direction == query.direction
            ]

        result = [
            signal
            for signal in result
            if signal.score >= query.minimum_score
        ]

        # ----------------------------------------
        # Sorting
        # ----------------------------------------

        sort_keys = {

            "score":
                lambda signal: signal.score,

            "distance":
                lambda signal: signal.distance,

            "time":
                lambda signal: signal.time,

            "symbol":
                lambda signal: signal.symbol,

            "strategy":
                lambda signal: signal.strategy,

            "direction":
                lambda signal: signal.direction,

            "price_low":
                lambda signal: signal.price_low,

            "price_high":
                lambda signal: signal.price_high,

        }

        key = sort_keys.get(
            query.sort_by,
            sort_keys["score"],
        )

        result.sort(
            key=key,
            reverse=query.descending,
        )

        # ----------------------------------------
        # Limit
        # ----------------------------------------

        if query.limit is not None:

            result = result[: query.limit]

        return result