from smartmoney.trading.execution import (
    ExecutionResult,
    ExecutionStatus,
)
from smartmoney.trading.trade_plan import TradePlan
from smartmoney.trading.broker_executor import BrokerExecutor
from smartmoney.trading.mt5_order_request import (
    build_mt5_order_request,
    build_real_mt5_order_request,
)
from smartmoney.trading.mt5_volume import calculate_mt5_volume

class MT5BrokerExecutor(BrokerExecutor):
    """
    Broker executor backed by an injected MT5 client.

    The MT5 client is injected so execution can be tested
    without connecting to a real terminal.
    """

    def __init__(
        self,
        mt5_client,
        volume: float = 1.0,
        success_retcode: int = 10009,
        use_real_request: bool = False,
        position_size_plan=None,
    ) -> None:
        self.mt5_client = mt5_client
        self.volume = (
            position_size_plan.position_size
            if position_size_plan is not None
            else volume
        )
        self.position_size_plan = position_size_plan
        self.use_real_request = use_real_request
        if success_retcode <= 0:
            raise ValueError(
                "Success retcode must be positive"
            )
        self.success_retcode = success_retcode
    def initialize(self) -> bool:
        return self.mt5_client.initialize()

    def shutdown(self) -> bool:
        return self.mt5_client.shutdown()

    def execute(
        self,
        plan: TradePlan,
    ) -> ExecutionResult:
        try:
            if self.use_real_request:
                market_price = self.mt5_client.market_price(
                    plan.symbol,
                )

                if plan.direction.value == "buy":
                    price = market_price["ask"]
                else:
                    price = market_price["bid"]

                symbol_info = self.mt5_client.symbol_info(plan.symbol)
                if self.position_size_plan is not None:
                    volume = calculate_mt5_volume(
                        risk_amount=self.position_size_plan.risk_amount,
                        stop_distance=self.position_size_plan.stop_distance,
                        trade_tick_value=symbol_info.trade_tick_value,
                        trade_tick_size=symbol_info.trade_tick_size,
                        volume_step=symbol_info.volume_step,
                        volume_min=symbol_info.volume_min,
                        volume_max=symbol_info.volume_max,
                    )
                else:
                    volume = self.volume
                request = build_real_mt5_order_request(
                    plan=plan,
                    volume=volume,
                    price=price,
                    type_filling=0 if symbol_info.filling_mode & 1 else 1,
                )
            else:
                volume = self.volume

                if self.position_size_plan is not None:
                    symbol_info = self.mt5_client.symbol_info(plan.symbol)
                    volume = calculate_mt5_volume(
                        risk_amount=self.position_size_plan.risk_amount,
                        stop_distance=self.position_size_plan.stop_distance,
                        trade_tick_value=symbol_info.trade_tick_value,
                        trade_tick_size=symbol_info.trade_tick_size,
                        volume_step=symbol_info.volume_step,
                        volume_min=symbol_info.volume_min,
                        volume_max=symbol_info.volume_max,
                    )

                request = build_mt5_order_request(
                    plan=plan,
                    volume=volume,
                )
            check_result = self.mt5_client.order_check(request)

            if check_result["retcode"] != 10009:
                return ExecutionResult(
                    status=ExecutionStatus.REJECTED,
                    plan=plan,
                    message=check_result.get("comment", "Order check failed"),
                )
            success = self.mt5_client.send_order(request)
        except Exception as exc:
            return ExecutionResult(
                status=ExecutionStatus.REJECTED,
                plan=plan,
                message=str(exc),
            )

        if isinstance(success, dict):
            retcode = success.get("retcode")

            if retcode != self.success_retcode:
                return ExecutionResult(
                    status=ExecutionStatus.REJECTED,
                    plan=plan,
                    message=success.get(
                        "comment",
                        "MT5 order rejected",
                    ),
                    broker_result=success,
                )

        if not success:
            return ExecutionResult(
                status=ExecutionStatus.REJECTED,
                plan=plan,
                message="MT5 order rejected",
                broker_result=success,
            )

        return ExecutionResult(
            status=ExecutionStatus.EXECUTED,
            plan=plan,
            message="MT5 order executed",
            broker_result=success,
        )