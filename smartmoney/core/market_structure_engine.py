from smartmoney.core.context import MarketContext


class MarketStructureEngine:
    """
    Maintains the current structural state
    of the market.

    This class will become the single source of truth
    for BOS / CHOCH / Trend.
    """

    def update(
        self,
        context: MarketContext,
    ) -> None:

        # implemented in next commits
        return