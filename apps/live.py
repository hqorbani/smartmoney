from smartmoney.scoring.engine import ScoreEngine

from smartmoney.scoring.orderblock import OrderBlockScore
from smartmoney.scoring.fvg import ActiveFVGScore

from smartmoney.config import Config

from smartmoney.core.mt5 import MT5DataProvider
from smartmoney.core.context_manager import ContextManager
from smartmoney.core.engine import AnalyzerEngine
from smartmoney.core.scanner_engine import ScannerEngine
from smartmoney.core.scheduler import Scheduler

from smartmoney.outputs.output_engine import OutputEngine
from smartmoney.outputs.console import ConsoleOutput
from smartmoney.outputs.csv_output import CsvOutput

from smartmoney.analyzers.swing import SwingAnalyzer
from smartmoney.analyzers.fvg import FVGAnalyzer
from smartmoney.analyzers.fvg_lifecycle import FVGLifecycleAnalyzer
from smartmoney.analyzers.orderblock import OrderBlockAnalyzer

from smartmoney.scanners.active_fvg import ActiveFVGScanner
from smartmoney.scanners.orderblock_active_fvg import (
    OrderBlockActiveFVGScanner,
)


def main():

    # ==================================================
    # Provider
    # ==================================================

    provider = MT5DataProvider()

    # ==================================================
    # Context
    # ==================================================

    context_manager = ContextManager()

    # ==================================================
    # Analyzer Engine
    # ==================================================

    analyzer_engine = AnalyzerEngine()

    analyzer_engine.add(SwingAnalyzer())
    analyzer_engine.add(FVGAnalyzer())
    analyzer_engine.add(FVGLifecycleAnalyzer())
    analyzer_engine.add(OrderBlockAnalyzer())

    # ==================================================
    # Scanner Engine
    # ==================================================

    scanner_engine = ScannerEngine()

    scanner_engine.add(
        ActiveFVGScanner()
    )

    scanner_engine.add(
        OrderBlockActiveFVGScanner()
    )
    # ==================================================
    # Score Engine
    # ==================================================

    score_engine = ScoreEngine()

    score_engine.add(
        OrderBlockScore()
    )

    score_engine.add(
        ActiveFVGScore()
    )
    # ==================================================
    # Output Engine
    # ==================================================

    output_engine = OutputEngine()

    output_engine.add(
        ConsoleOutput()
    )

    output_engine.add(
        CsvOutput()
    )

    # ==================================================
    # Scheduler
    # ==================================================

    scheduler = Scheduler(
        provider=provider,
        context_manager=context_manager,

        analyzer_engine=analyzer_engine,
        scanner_engine=scanner_engine,
        score_engine=score_engine,
        output_engine=output_engine,

        symbols=Config.SYMBOLS,
        timeframes=Config.TIMEFRAMES,

        candle_count=Config.HISTORY_BARS,

        interval=Config.SCAN_INTERVAL,
    )

    scheduler.start()


if __name__ == "__main__":

    main()