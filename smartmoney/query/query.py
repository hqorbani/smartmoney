from dataclasses import dataclass


@dataclass(slots=True)
class Query:

    # -----------------------------
    # Filters
    # -----------------------------

    symbol: str | None = None

    timeframe: int | None = None

    strategy: str | None = None

    direction: str | None = None

    minimum_score: float = 0.0

    # -----------------------------
    # Sorting
    # -----------------------------

    sort_by: str = "distance"

    descending: bool = False

    # -----------------------------
    # Result
    # -----------------------------

    limit: int | None = 20