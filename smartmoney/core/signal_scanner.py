from smartmoney.config import Config
from smartmoney.core.context_manager import ContextManager
from smartmoney.core.engine import AnalyzerEngine
from smartmoney.core.mt5 import MT5DataProvider
from smartmoney.core.scanner_engine import ScannerEngine
from smartmoney.core.market_structure_engine import MarketStructureEngine
from smartmoney.core.structure_event_engine import StructureEventEngine
from smartmoney.models.signal import SignalDirection
from smartmoney.services.distance_service import DistanceService


class SignalScanner:

    def __init__(
        self,
        provider: MT5DataProvider,
        context_manager: ContextManager,
        analyzer_engine: AnalyzerEngine,
        scanner_engine: ScannerEngine,
        market_structure_engine: MarketStructureEngine,
        structure_event_engine: StructureEventEngine,
        distance_service: DistanceService,
        symbols: list[str],
        timeframes: list[int],
        candle_count: int,
    ) -> None:
        self.provider = provider
        self.context_manager = context_manager
        self.analyzer_engine = analyzer_engine
        self.scanner_engine = scanner_engine
        self.market_structure_engine = market_structure_engine
        self.structure_event_engine = structure_event_engine
        self.distance_service = distance_service
        self.symbols = symbols
        self.timeframes = timeframes
        self.candle_count = candle_count

    def scan(self):
        all_signals = []

        for symbol in self.symbols:
            for timeframe in self.timeframes:

                df = self.provider.fetch_rates(
                    symbol=symbol,
                    timeframe=timeframe,
                    count=self.candle_count + 1,
                )

                df = df.iloc[:-1].copy()

                context = self.context_manager.update(
                    symbol=symbol,
                    timeframe=timeframe,
                    df=df,
                )

                self.analyzer_engine.run(context)

                events = self.structure_event_engine.run(context)

                self.market_structure_engine.update(
                    context,
                    events,
                )

                signals = self.scanner_engine.run(context)

                for signal in signals:

                    if (
                        signal.orderblock is not None
                        and signal.fvg is not None
                    ):
                        original_context_signal = context.signal
                        original_entry_plan = context.entry_plan
                        original_stop_loss_plan = context.stop_loss_plan
                        original_take_profit_plan = context.take_profit_plan
                        original_trade_plan = context.trade_plan
                        original_position_size_plan = (
                            context.position_size_plan
                        )
                        original_direction = signal.direction

                        if signal.direction == "BUY":
                            signal.direction = SignalDirection.BUY

                        elif signal.direction == "SELL":
                            signal.direction = SignalDirection.SELL

                        context.signal = signal

                        self.analyzer_engine.run_from_priority(
                            context,
                            50,
                        )

                        signal.entry_plan = context.entry_plan
                        signal.stop_loss_plan = context.stop_loss_plan
                        signal.take_profit_plan = context.take_profit_plan
                        signal.trade_plan = context.trade_plan
                        signal.position_size_plan = (
                            context.position_size_plan
                        )

                        signal.direction = original_direction

                        context.signal = original_context_signal
                        context.entry_plan = original_entry_plan
                        context.stop_loss_plan = original_stop_loss_plan
                        context.take_profit_plan = original_take_profit_plan
                        context.trade_plan = original_trade_plan
                        context.position_size_plan = (
                            original_position_size_plan
                        )

                    self.distance_service.calculate(
                        signal,
                        self.provider.get_current_price(signal.symbol),
                    )

                all_signals.extend(signals)

        return all_signals