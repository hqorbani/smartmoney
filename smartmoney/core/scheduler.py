import time

from smartmoney.core.context_manager import ContextManager
from smartmoney.core.engine import AnalyzerEngine
from smartmoney.core.mt5 import MT5DataProvider
from smartmoney.core.scanner_engine import ScannerEngine
from smartmoney.outputs.output_engine import OutputEngine
from smartmoney.scoring.engine import ScoreEngine


class Scheduler:

    def __init__(
        self,
        provider: MT5DataProvider,
        context_manager: ContextManager,
        analyzer_engine: AnalyzerEngine,
        scanner_engine: ScannerEngine,
        output_engine: OutputEngine,
        score_engine: ScoreEngine,
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

        self.symbols = symbols
        self.timeframes = timeframes
        self.candle_count = candle_count

        self.interval = interval

        self._running = False

    def start(self):

        self.provider.connect()

        self._running = True

        try:

            while self._running:

                self.run_once()

                time.sleep(self.interval)

        finally:

            self.provider.shutdown()

    def stop(self):

        self._running = False

    def run_once(self):

        all_signals = []

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

                # -----------------------------
                # Analyze
                # -----------------------------

                self.analyzer_engine.run(context)

                # -----------------------------
                # Scan
                # -----------------------------

                signals = self.scanner_engine.run(context)

                # -----------------------------
                # Score
                # -----------------------------

                for signal in signals:

                    self.score_engine.calculate(
                        signal,
                        context,
                    )

                all_signals.extend(signals)

        # -----------------------------
        # Publish Outputs
        # -----------------------------

        self.output_engine.publish(all_signals)