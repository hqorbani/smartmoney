import numpy as np
import pandas as pd
from unittest.mock import patch

from smartmoney.core.mt5 import MT5DataProvider


def test_fetch_rates_preserves_mt5_rate_order():
    raw_rates = np.array(
        [
            (1735689720, 100.0, 101.0, 99.0, 100.5, 10, 1, 10),
            (1735689660, 99.0, 100.0, 98.0, 99.5, 11, 1, 11),
            (1735689600, 98.0, 99.0, 97.0, 98.5, 12, 1, 12),
        ],
        dtype=[
            ("time", "i8"),
            ("open", "f8"),
            ("high", "f8"),
            ("low", "f8"),
            ("close", "f8"),
            ("tick_volume", "i8"),
            ("spread", "i8"),
            ("real_volume", "i8"),
        ],
    )

    provider = MT5DataProvider()

    with (
        patch(
            "smartmoney.core.mt5.mt5.symbol_select",
            return_value=True,
        ),
        patch(
            "smartmoney.core.mt5.mt5.copy_rates_from_pos",
            return_value=raw_rates,
        ),
    ):
        result = provider.fetch_rates(
            symbol="NAS100",
            timeframe=1,
            count=3,
        )

    assert list(result["time"]) == [
        pd.Timestamp("2025-01-01 00:02:00"),
        pd.Timestamp("2025-01-01 00:01:00"),
        pd.Timestamp("2025-01-01 00:00:00"),
    ]