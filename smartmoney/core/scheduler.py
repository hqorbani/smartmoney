import time
from smartmoney.trading.execution import ExecutionStatus
from smartmoney.config import Config
from smartmoney.core.context_manager import ContextManager
from smartmoney.core.engine import AnalyzerEngine
from smartmoney.core.mt5 import MT5DataProvider
from smartmoney.core.scanner_engine import ScannerEngine
from smartmoney.trading.mt5_broker_executor import MT5BrokerExecutor
from smartmoney.outputs.output_engine import OutputEngine
from smartmoney.query.query import Query
from smartmoney.query.query_engine import QueryEngine
from smartmoney.repository.signal_repository import SignalRepository
from smartmoney.scoring.engine import ScoreEngine
from smartmoney.services.distance_service import DistanceService
from smartmoney.models.signal import SignalDirection
from smartmoney.core.logging import get_logger

from smartmoney.core.market_structure_engine import (
    MarketStructureEngine
)

from smartmoney.core.structure_event_engine import StructureEventEngine
from smartmoney.models.orderblock import (
    Attempt1Status,
    Attempt2Status,
    OrderBlockStatus,
)
from smartmoney.services.zone_entry_service import ZoneEntryService

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
        executor=None,
    ) -> None:
        self.logger = get_logger("scheduler")
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
        self.zone_entry_service = ZoneEntryService()
        self.symbols = symbols
        self.timeframes = timeframes
        self.candle_count = candle_count

        self.interval = interval
        self.executor = executor
        self._executed_trade_keys = set()
        self._running = False

    # ---------------------------------------------------------
    def _has_active_position(self, symbol: str) -> bool:
        if self.executor is None:
            return False

        positions = self.executor.mt5_client.positions_get(
            symbol=symbol,
        )

        return bool(positions)
    
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
        self.logger.info("Scheduler cycle started")
        all_signals = []

        # -----------------------------------------
        # Scan all markets
        # -----------------------------------------

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
                tick = self.provider.get_current_tick(symbol)

                context.current_bid = tick.bid
                context.current_ask = tick.ask
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
                        original_position_size_plan = context.position_size_plan
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

                        setattr(
                            signal,
                            "entry_plan",
                            context.entry_plan,
                        )

                        setattr(
                            signal,
                            "stop_loss_plan",
                            context.stop_loss_plan,
                        )

                        setattr(
                            signal,
                            "take_profit_plan",
                            context.take_profit_plan,
                        )

                        setattr(
                            signal,
                            "trade_plan",
                            context.trade_plan,
                        )

                        setattr(
                            signal,
                            "position_size_plan",
                            context.position_size_plan,
                        )

                        signal.direction = original_direction

                        context.signal = original_context_signal
                        context.entry_plan = original_entry_plan
                        context.stop_loss_plan = original_stop_loss_plan
                        context.take_profit_plan = original_take_profit_plan
                        context.trade_plan = original_trade_plan
                        context.position_size_plan = original_position_size_plan

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
        if self.executor is not None:
            executed_this_cycle = False
            for signal in queried_signals:
                trade_plan = getattr(signal, "trade_plan", None)
                position_size_plan = getattr(signal, "position_size_plan", None)
                entry_plan = getattr(signal, "entry_plan", None)
                orderblock = getattr(signal, "orderblock", None)

                if entry_plan is None or orderblock is None:
                    continue

                current_price = getattr(signal, "current_price", None)
                if current_price is None:
                    continue

                if trade_plan is None or position_size_plan is None:
                    continue

                trade_key = (
                    trade_plan.symbol,
                    trade_plan.timeframe,
                    trade_plan.direction.value,
                    trade_plan.orderblock_index,
                )

                if executed_this_cycle:
                    break

                if trade_key in self._executed_trade_keys:
                    continue

                attempt_zone = None

                initial_zone = next(
                    zone
                    for zone in entry_plan.zones
                    if zone.name == "INITIAL"
                )
                middle_zone = next(
                    zone
                    for zone in entry_plan.zones
                    if zone.name == "MIDDLE"
                )

                zone_entry_price = (
                    context.current_ask
                    if signal.direction == SignalDirection.BUY
                    else context.current_bid
                )

                if zone_entry_price is None:
                    continue

                if orderblock.attempt1_status == Attempt1Status.NOT_USED:
                    if self.zone_entry_service.is_first_entry(
                        orderblock,
                        "INITIAL",
                        zone_entry_price,
                        initial_zone.price_low,
                        initial_zone.price_high,
                    ):
                        attempt_zone = "INITIAL"

                elif (
                    orderblock.attempt1_status == Attempt1Status.FAILED
                    and orderblock.attempt2_status == Attempt2Status.AVAILABLE
                ):
                    if self.zone_entry_service.is_first_entry(
                        orderblock,
                        "MIDDLE",
                        zone_entry_price,
                        middle_zone.price_low,
                        middle_zone.price_high,
                    ):
                        attempt_zone = "MIDDLE"

                if attempt_zone is None:
                    continue

                if self._has_active_position(trade_plan.symbol):
                    self.logger.info(
                        "Entry skipped: active position already exists for this symbol."
                    )

                    if attempt_zone == "INITIAL":
                        orderblock.attempt1_status = Attempt1Status.FAILED
                        orderblock.attempt2_status = Attempt2Status.AVAILABLE
                    else:
                        orderblock.attempt2_status = Attempt2Status.FAILED
                        orderblock.status = OrderBlockStatus.CONSUMED

                    continue

                signal_executor = MT5BrokerExecutor(
                    mt5_client=self.executor.mt5_client,
                    use_real_request=True,
                    position_size_plan=position_size_plan,
                )

                result = signal_executor.execute(trade_plan)
                self.logger.info(
                    "Trade execution | signal_id=%s | symbol=%s | timeframe=%s | "
                    "direction=%s | entry=%s | stop_loss=%s | take_profit=%s | "
                    "volume=%s | status=%s | broker_result=%s",
                    getattr(signal, "signal_id", None),
                    trade_plan.symbol,
                    trade_plan.timeframe,
                    trade_plan.direction.value,
                    trade_plan.entry_price,
                    trade_plan.stop_loss,
                    trade_plan.take_profit,
                    position_size_plan.position_size,
                    result.status.value,
                    result.broker_result,
                )

                if attempt_zone == "INITIAL":
                    if result.status == ExecutionStatus.EXECUTED:
                        orderblock.attempt1_status = Attempt1Status.SUCCESS
                        orderblock.status = OrderBlockStatus.CONSUMED
                    else:
                        orderblock.attempt1_status = Attempt1Status.FAILED
                        orderblock.attempt2_status = Attempt2Status.AVAILABLE

                elif attempt_zone == "MIDDLE":
                    if result.status == ExecutionStatus.EXECUTED:
                        orderblock.attempt2_status = Attempt2Status.SUCCESS
                    else:
                        orderblock.attempt2_status = Attempt2Status.FAILED

                    orderblock.status = OrderBlockStatus.CONSUMED

                if result.status == ExecutionStatus.EXECUTED:
                    self._executed_trade_keys.add(trade_key)
                    executed_this_cycle = True