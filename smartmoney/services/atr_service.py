import pandas as pd


class ATRService:
    """
    Calculates Average True Range (ATR) from OHLC candles.
    """

    def calculate(
        self,
        df: pd.DataFrame,
        period: int,
    ) -> pd.Series:

        if period <= 0:
            raise ValueError("ATR period must be positive")

        required_columns = {"high", "low", "close"}

        if not required_columns.issubset(df.columns):
            raise ValueError(
                "DataFrame must contain high, low, and close columns"
            )

        previous_close = df["close"].shift(1)

        true_range = pd.concat(
            [
                df["high"] - df["low"],
                (df["high"] - previous_close).abs(),
                (df["low"] - previous_close).abs(),
            ],
            axis=1,
        ).max(axis=1)

        return true_range.ewm(
            alpha=1 / period,
            adjust=False,
            min_periods=period,
        ).mean()