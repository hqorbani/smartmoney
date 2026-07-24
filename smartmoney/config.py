from dataclasses import dataclass

import MetaTrader5 as mt5


@dataclass(slots=True)
class Config:

    # ----------------------------
    # MT5
    # ----------------------------

    HISTORY_BARS = 100

    SCAN_INTERVAL = 3

    SYMBOLS = [
        "XAUUSD",
    ]

    TIMEFRAMES = [
        mt5.TIMEFRAME_M5,
    ]

    # ----------------------------
    # Swing
    # ----------------------------

    SWING_LEFT = 2
    SWING_RIGHT = 2

    # ----------------------------
    # FVG
    # ----------------------------

    MIN_FVG_SIZE = 0.1

    # ----------------------------
    # Query
    # ----------------------------

    SORT_BY = "distance"

    SORT_DESCENDING = False

    TOP_SIGNALS = 10

    MINIMUM_SCORE = 0.0

    # ----------------------------
    # Debug
    # ----------------------------

    PRINT_SWINGS = False

    PRINT_FVGS = False

    PRINT_ORDERBLOCKS = False