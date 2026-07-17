from smartmoney.core.context import MarketContext


class ContextManager:
    """
    Keeps one MarketContext per (symbol, timeframe).
    """

    def __init__(self) -> None:
        self._contexts: dict[tuple[str, int], MarketContext] = {}

    @staticmethod
    def _key(symbol: str, timeframe: int) -> tuple[str, int]:
        return symbol, timeframe

    def get(
        self,
        symbol: str,
        timeframe: int,
    ) -> MarketContext | None:
        """
        Return existing context or None.
        """
        return self._contexts.get(self._key(symbol, timeframe))

    def update(
        self,
        symbol: str,
        timeframe: int,
        df,
    ) -> MarketContext:
        """
        Create or update a MarketContext.
        """

        key = self._key(symbol, timeframe)

        context = self._contexts.get(key)

        if context is None:

            context = MarketContext(
                symbol=symbol,
                timeframe=timeframe,
                df=df,
            )

            self._contexts[key] = context

        else:

            context.df = df

        return context

    def remove(
        self,
        symbol: str,
        timeframe: int,
    ) -> None:

        self._contexts.pop(
            self._key(symbol, timeframe),
            None,
        )

    def clear(self) -> None:
        """
        Remove all contexts.
        """
        self._contexts.clear()

    def all(self) -> list[MarketContext]:
        """
        Return all active contexts.
        """
        return list(self._contexts.values())