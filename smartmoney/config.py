from dataclasses import dataclass

import MetaTrader5 as mt5


@dataclass(slots=True)
class Config:

    # ----------------------------
    # MT5
    # ----------------------------

    HISTORY_BARS = 500

    SCAN_INTERVAL = 3

    SYMBOLS = [
        "NAS100",
        "XAUUSD",
    ]

    TIMEFRAMES = [
        mt5.TIMEFRAME_M5,
        mt5.TIMEFRAME_M15,
    ]

    # ----------------------------
    # Swing
    # ----------------------------

    SWING_LEFT = 2
    SWING_RIGHT = 2

    # ----------------------------
    # FVG
    # ----------------------------

    MIN_FVG_SIZE = 0.0

    # ----------------------------
    # Debug
    # ----------------------------

    PRINT_SWINGS = False

    PRINT_FVGS = False

    PRINT_ORDERBLOCKS = False