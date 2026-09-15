from smartmoney.trading.execution import (
    ExecutionResult,
    ExecutionStatus,
)
from smartmoney.trading.trade_plan import TradePlan
from smartmoney.trading.broker_executor import BrokerExecutor


class MT5BrokerExecutor(BrokerExecutor):
    """
    Broker executor backed by an injected MT5 client.

    The MT5 client is injected so execution can be tested
    without connecting to a real terminal.
    """

    def __init__(self, mt5_client) -> None:
        self.mt5_client = mt5_client

    def execute(
        self,
        plan: TradePlan,
    ) -> ExecutionResult:
        try:
            success = self.mt5_client.send_order(plan)
        except Exception as exc:
            return ExecutionResult(
                status=ExecutionStatus.REJECTED,
                plan=plan,
                message=str(exc),
            )

        if not success:
            return ExecutionResult(
                status=ExecutionStatus.REJECTED,
                plan=plan,
                message="MT5 order rejected",
            )

        return ExecutionResult(
            status=ExecutionStatus.EXECUTED,
            plan=plan,
            message="MT5 order executed",
        )