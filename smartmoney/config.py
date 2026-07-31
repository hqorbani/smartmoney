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
    ]
    #----------
    #-SYMBOLS = [
    #-    "NAS100": 1,
    #-    "XAUUSD": 0.5,
    #-    "BITCOIN": 0.5,
    #-    "EURUSD": 0.0001,
    #-    "NZDCAD": 0.0001,
    #-    "AUDUSD": 0.0001,
    #-    "GBPUSD": 0.0001,
    #-]

    TIMEFRAMES = [
        mt5.TIMEFRAME_M1,
    ]

    # ----------------------------
    # Swing
    # ----------------------------

    SWING_LEFT = 2
    SWING_RIGHT = 2

    # ----------------------------
    # FVG
    # ----------------------------

    MIN_FVG_SIZE = 0.5

    # ----------------------------
    # Query
    # ----------------------------

    SORT_BY = "distance"

    SORT_DESCENDING = False

    TOP_SIGNALS = 40

    MINIMUM_SCORE = 0.0

    # ----------------------------
    # Debug
    # ----------------------------

    PRINT_SWINGS = True

    PRINT_FVGS = False

    PRINT_ORDERBLOCKS = False


    STRUCTURE_BREAK_MODE = "close"
    #-- close|wick