import pytest

from smartmoney.trading.broker_executor import BrokerExecutor
from smartmoney.trading.trade_plan import (
    TradeDirection,
    TradePlan,
)
from smartmoney.trading.execution import ExecutionResult, ExecutionStatus

def test_broker_executor_is_an_abstract_interface():
    with pytest.raises(TypeError):
        BrokerExecutor()


def test_broker_executor_defines_execute_contract():
    assert hasattr(BrokerExecutor, "execute")

def test_broker_executor_implementation_can_execute_trade_plan():
    class FakeBrokerExecutor(BrokerExecutor):
        def execute(
            self,
            plan: TradePlan,
        ) -> ExecutionResult:
            return ExecutionResult(
                status=ExecutionStatus.EXECUTED,
                plan=plan,
                message="Fake broker executed",
            )

    plan = TradePlan(
        symbol="NAS100",
        timeframe=1,
        direction=TradeDirection.BUY,
        entry_price=29442.3,
        stop_loss=29440.0,
        take_profit=29446.9,
        risk_distance=2.3,
        orderblock_index=21,
    )

    executor = FakeBrokerExecutor()

    result = executor.execute(plan)

    assert result.status == ExecutionStatus.EXECUTED
    assert result.plan == plan
    assert result.message == "Fake broker executed"    