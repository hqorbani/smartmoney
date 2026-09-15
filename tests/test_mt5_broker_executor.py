from smartmoney.trading.execution import ExecutionResult, ExecutionStatus
from smartmoney.trading.mt5_broker_executor import MT5BrokerExecutor
from smartmoney.trading.trade_plan import TradeDirection, TradePlan


def test_mt5_broker_executor_returns_executed_result():
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

    class FakeMT5:
        def send_order(self, plan):
            return True

    executor = MT5BrokerExecutor(FakeMT5())

    result = executor.execute(plan)

    assert isinstance(result, ExecutionResult)
    assert result.status == ExecutionStatus.EXECUTED
    assert result.plan == plan

def test_mt5_broker_executor_returns_rejected_result_when_order_fails():
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

    class FakeMT5:
        def send_order(self, plan):
            return False

    executor = MT5BrokerExecutor(FakeMT5())

    result = executor.execute(plan)

    assert result.status == ExecutionStatus.REJECTED
    assert result.plan == plan
    assert result.message == "MT5 order rejected"

def test_mt5_broker_executor_returns_rejected_result_when_mt5_raises():
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

    class FakeMT5:
        def send_order(self, plan):
            raise RuntimeError("MT5 connection failed")

    executor = MT5BrokerExecutor(FakeMT5())

    result = executor.execute(plan)

    assert result.status == ExecutionStatus.REJECTED
    assert result.plan == plan
    assert result.message == "MT5 connection failed"      