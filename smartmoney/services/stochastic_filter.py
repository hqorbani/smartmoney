
import numpy as np
import talib

from smartmoney.config import Config


class StochasticFilter:
    @staticmethod
    def evaluate(df, direction) -> tuple[bool, float | None, float | None, str]:
        if not Config.ENABLE_STOCHASTIC_FILTER:
            return True, None, None, "FILTER_DISABLED"

        required_columns = {"high", "low", "close"}
        if df is None or not required_columns.issubset(df.columns):
            return False, None, None, "MISSING_DATA_OR_COLUMNS"

        try:
            required_length = (
                Config.STOCHASTIC_K_PERIOD
                + Config.STOCHASTIC_SLOWING
                + Config.STOCHASTIC_D_PERIOD
                - 2
            )

            if len(df) < required_length:
                return False, None, None, "INSUFFICIENT_DATA"

            high = df["high"].to_numpy(dtype=float)
            low = df["low"].to_numpy(dtype=float)
            close = df["close"].to_numpy(dtype=float)

            slow_k, slow_d = talib.STOCH(
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
            d_value = slow_d[-1]

            k = float(k_value) if np.isfinite(k_value) else None
            d = float(d_value) if np.isfinite(d_value) else None

            # Preserve the existing entry rules: decisions use %K only.
            if k is None:
                return False, k, d, "INVALID_K_VALUE"

            direction_value = getattr(direction, "value", direction)
            direction_value = str(direction_value).upper()

            if direction_value == "BUY":
                allowed = k < Config.STOCHASTIC_OVERBOUGHT
                reason = (
                    "WITHIN_ALLOWED_RANGE"
                    if allowed
                    else "OVERBOUGHT"
                )
                return allowed, k, d, reason

            if direction_value == "SELL":
                allowed = k > Config.STOCHASTIC_OVERSOLD
                reason = (
                    "WITHIN_ALLOWED_RANGE"
                    if allowed
                    else "OVERSOLD"
                )
                return allowed, k, d, reason

            return False, k, d, "INVALID_DIRECTION"

        except (TypeError, ValueError, KeyError, IndexError):
            return False, None, None, "CALCULATION_ERROR"

    @staticmethod
    def is_entry_allowed(df, direction) -> bool:
        allowed, _, _, _ = StochasticFilter.evaluate(df, direction)
        return allowed
