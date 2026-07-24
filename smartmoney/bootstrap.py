from smartmoney.config import Config

from smartmoney.core.discovery import discover
from smartmoney.core.context import MarketContext
from smartmoney.core.context_manager import ContextManager
from smartmoney.core.engine import AnalyzerEngine
from smartmoney.core.mt5 import MT5DataProvider
from smartmoney.core.scheduler import Scheduler
from smartmoney.core.scanner_engine import ScannerEngine

from smartmoney.analyzers.base import Analyzer
from smartmoney.scanners.base import Scanner
from smartmoney.scoring.base import ScoreRule
from smartmoney.outputs.base import Output

from smartmoney.scoring.engine import ScoreEngine
from smartmoney.outputs.output_engine import OutputEngine

from smartmoney.visualization.chart import ChartVisualizer

from smartmoney.repository.signal_repository import SignalRepository
from smartmoney.query.query_engine import QueryEngine

from smartmoney.services.distance_service import DistanceService
from smartmoney.core.market_structure_engine import (
    MarketStructureEngine,
)

from smartmoney.core.structure_event_engine import (
    StructureEventEngine,
)

# ==========================================================
# Provider
# ==========================================================

def create_provider() -> MT5DataProvider:

    return MT5DataProvider()


# ==========================================================
# Context Manager
# ==========================================================

def create_context_manager() -> ContextManager:

    return ContextManager()


# ==========================================================
# Analyzer Engine
# ==========================================================

def _create_analyzer_engine() -> AnalyzerEngine:

    engine = AnalyzerEngine()

    analyzers = discover(
        "smartmoney.analyzers",
        Analyzer,
    )

    for analyzer in analyzers:

        engine.add(analyzer)

    return engine


# ==========================================================
# Scanner Engine
# ==========================================================

def _create_scanner_engine() -> ScannerEngine:

    engine = ScannerEngine()

    scanners = discover(
        "smartmoney.scanners",
        Scanner,
    )

    for scanner in scanners:

        engine.add(scanner)

    return engine


# ==========================================================
# Score Engine
# ==========================================================

def _create_score_engine() -> ScoreEngine:

    engine = ScoreEngine()

    rules = discover(
        "smartmoney.scoring",
        ScoreRule,
    )

    for rule in rules:

        engine.add(rule)

    return engine


# ==========================================================
# Output Engine
# ==========================================================

def _create_output_engine() -> OutputEngine:

    engine = OutputEngine()

    outputs = discover(
        "smartmoney.outputs",
        Output,
    )

    for output in outputs:

        engine.add(output)

    return engine


# ==========================================================
# Scheduler
# ==========================================================

def create_live_scheduler() -> Scheduler:

    repository = SignalRepository()
    query_engine = QueryEngine()
    distance_service = DistanceService()

    provider = create_provider()

    scheduler = Scheduler(

        provider=provider,

        context_manager=create_context_manager(),

        analyzer_engine=_create_analyzer_engine(),

        scanner_engine=_create_scanner_engine(),

        output_engine=_create_output_engine(),

        score_engine=_create_score_engine(),

        structure_event_engine=create_structure_event_engine(),

        market_structure_engine=create_market_structure_engine(),

        repository=repository,

        query_engine=query_engine,

        distance_service=distance_service,

        symbols=Config.SYMBOLS,

        timeframes=Config.TIMEFRAMES,

        candle_count=Config.HISTORY_BARS,

        interval=Config.SCAN_INTERVAL,

    )

    return scheduler


# ==========================================================
# Chart Context
# ==========================================================

def create_chart_context(
    symbol: str,
    timeframe: int,
) -> MarketContext:

    provider = create_provider()

    provider.connect()

    try:

        df = provider.fetch_rates(
            symbol=symbol,
            timeframe=timeframe,
            count=Config.HISTORY_BARS,
        )

    finally:

        provider.shutdown()

    context = MarketContext(
        symbol=symbol,
        timeframe=timeframe,
        df=df,
    )

    analyzer_engine = _create_analyzer_engine()

    analyzer_engine.run(context)

    return context


def create_market_structure_engine() -> MarketStructureEngine:
    return MarketStructureEngine()


# ==========================================================
# Structure Event Engine
# ==========================================================

def create_structure_event_engine() -> StructureEventEngine:

    return StructureEventEngine()