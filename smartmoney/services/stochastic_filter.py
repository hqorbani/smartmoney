import numpy as np
import talib

from smartmoney.config import Config


class StochasticFilter:
    @staticmethod
    def is_entry_allowed(df, direction) -> bool:
        if not Config.ENABLE_STOCHASTIC_FILTER:
            return True

        required_columns = {"high", "low", "close"}
        if df is None or not required_columns.issubset(df.columns):
            return False

        try:
            high = df["high"].to_numpy(dtype=float)
            low = df["low"].to_numpy(dtype=float)
            close = df["close"].to_numpy(dtype=float)

            if len(df) < (
                Config.STOCHASTIC_K_PERIOD
                + Config.STOCHASTIC_SLOWING
                + Config.STOCHASTIC_D_PERIOD
                - 2
            ):
                return False

            slow_k, _ = talib.STOCH(
                high,
                low,
                close,
                fastk_period=Config.STOCHASTIC_K_PERIOD,
                slowk_period=Config.STOCHASTIC_SLOWING,
                slowk_matype=0,
                slowd_period=Config.STOCHASTIC_D_PERIOD,
                slowd_matype=0,
            )

            k_value = slow_k[-1]

            if not np.isfinite(k_value):
                return False

            direction_value = getattr(direction, "value", direction)
            direction_value = str(direction_value).upper()

            if direction_value == "BUY":
                return bool(k_value < Config.STOCHASTIC_OVERBOUGHT)

            if direction_value == "SELL":
                return bool(k_value > Config.STOCHASTIC_OVERSOLD)

            return False

        except (TypeError, ValueError, KeyError):
            return False