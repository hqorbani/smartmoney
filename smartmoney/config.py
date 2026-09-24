from dataclasses import dataclass
import MetaTrader5 as mt5
from smartmoney.symbol_config import SYMBOL_CONFIG

@dataclass(slots=True)
class Config:

    # ----------------------------
    # MT5
    # ----------------------------
    RISK_PERCENT = 1.0
    
    HISTORY_BARS = 600

    SCAN_INTERVAL = 3

    SYMBOLS = list(SYMBOL_CONFIG.keys())
    #----------

    TIMEFRAMES = [
        mt5.TIMEFRAME_M1,
        mt5.TIMEFRAME_M3,
        mt5.TIMEFRAME_M5,
        # mt5.TIMEFRAME_M15,
        # mt5.TIMEFRAME_H1
    ]

    # ----------------------------
    # Swing
    # ----------------------------

    SWING_LEFT = 2
    SWING_RIGHT = 2


    # ----------------------------
    # Query
    # ----------------------------

    SORT_BY = "distance"

    SORT_DESCENDING = False

    TOP_SIGNALS = 20

    MINIMUM_SCORE = 0.0



    RR_RATIO = 2.0
    ATR_PERIOD = 11
    
    # ----------------------------
    # Debug
    # ----------------------------

    PRINT_SWINGS = True

    PRINT_FVGS = False

    PRINT_ORDERBLOCKS = False


    STRUCTURE_BREAK_MODE = "close"
    #-- close|wick


    # ----------------------------
    # BackTest
    # ----------------------------
    EXPORT_BACKTEST_TRADE_DETAILS = False