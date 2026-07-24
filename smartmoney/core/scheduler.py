import time

from smartmoney.config import Config
from smartmoney.core.context_manager import ContextManager
from smartmoney.core.engine import AnalyzerEngine
from smartmoney.core.mt5 import MT5DataProvider
from smartmoney.core.scanner_engine import ScannerEngine

from smartmoney.outputs.output_engine import OutputEngine
from smartmoney.query.query import Query
from smartmoney.query.query_engine import QueryEngine
from smartmoney.repository.signal_repository import SignalRepository
from smartmoney.scoring.engine import ScoreEngine
from smartmoney.services.distance_service import DistanceService


from smartmoney.core.market_structure_engine import (
    MarketStructureEngine
)

from smartmoney.core.structure_event_engine import StructureEventEngine

class Scheduler:

    def __init__(
        self,
        provider: MT5DataProvider,
        context_manager: ContextManager,
        analyzer_engine: AnalyzerEngine,
        scanner_engine: ScannerEngine,
        output_engine: OutputEngine,
        score_engine: ScoreEngine,
        market_structure_engine: MarketStructureEngine,
        structure_event_engine: StructureEventEngine,
        repository: SignalRepository,
        query_engine: QueryEngine,
        distance_service: DistanceService,
        symbols: list[str],
        timeframes: list[int],
        candle_count: int,
        interval: int = 3,
    ) -> None:

        self.provider = provider
        self.context_manager = context_manager

        self.analyzer_engine = analyzer_engine
        self.scanner_engine = scanner_engine
        self.output_engine = output_engine
        self.score_engine = score_engine
        self.market_structure_engine = market_structure_engine
        self.structure_event_engine = structure_event_engine
        self.repository = repository
        self.query_engine = query_engine
        self.distance_service = distance_service
        
        self.symbols = symbols
        self.timeframes = timeframes
        self.candle_count = candle_count

        self.interval = interval

        self._running = False

    # ---------------------------------------------------------

    def start(self):

        self.provider.connect()

        self._running = True

        try:

            while self._running:

                self.run_once()

                time.sleep(self.interval)

        finally:

            self.provider.shutdown()

    # ---------------------------------------------------------

    def stop(self):

        self._running = False

    # ---------------------------------------------------------

    def run_once(self):

        all_signals = []

        # -----------------------------------------
        # Scan all markets
        # -----------------------------------------

        for symbol in self.symbols:

            for timeframe in self.timeframes:

                df = self.provider.fetch_rates(
                    symbol=symbol,
                    timeframe=timeframe,
                    count=self.candle_count,
                )

                context = self.context_manager.update(
                    symbol=symbol,
                    timeframe=timeframe,
                    df=df,
                )

                # ----------------------------
                # Analyze
                # ----------------------------

                self.analyzer_engine.run(context)

                events = self.structure_event_engine.run(
                    context,
                )

                self.market_structure_engine.update(
                    context,
                    events,
                ) 
                # ----------------------------
                # Scan
                # ----------------------------

                signals = self.scanner_engine.run(context)

                # ----------------------------
                # Score
                # ----------------------------

                for signal in signals:

                    self.score_engine.calculate(
                        signal,
                        context,
                    )

                    current_price = self.provider.get_current_price(
                        signal.symbol,
                    )

                    self.distance_service.calculate(
                        signal,
                        current_price,
                    )

                all_signals.extend(signals)

        # -----------------------------------------
        # Repository
        # -----------------------------------------

        self.repository.replace(all_signals)

        # -----------------------------------------
        # Query
        # -----------------------------------------

        query = Query(

            minimum_score=Config.MINIMUM_SCORE,

            sort_by=Config.SORT_BY,

            descending=Config.SORT_DESCENDING,

            limit=Config.TOP_SIGNALS,

        )

        queried_signals = self.query_engine.query(

            self.repository.all(),

            query,

        )

        # -----------------------------------------
        # Outputs
        # -----------------------------------------

        self.output_engine.publish(
            queried_signals,
        )