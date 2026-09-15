from smartmoney.trading.execution import ExecutionResult, ExecutionStatus
from smartmoney.trading.mt5_broker_executor import MT5BrokerExecutor
from smartmoney.trading.trade_plan import TradeDirection, TradePlan
import pytest

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

def test_mt5_broker_executor_sends_order_request():
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

    class FakeMT5Client:
        def __init__(self):
            self.received_request = None

        def send_order(self, request):
            self.received_request = request
            return True

    client = FakeMT5Client()
    executor = MT5BrokerExecutor(client)

    result = executor.execute(plan)

    assert result.status == ExecutionStatus.EXECUTED
    assert client.received_request == {
        "symbol": "NAS100",
        "volume": 1.0,
        "direction": "buy",
        "entry_price": 29442.3,
        "stop_loss": 29440.0,
        "take_profit": 29446.9,
    }

def test_mt5_broker_executor_rejects_non_positive_volume():
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

    class FakeMT5Client:
        def send_order(self, request):
            raise AssertionError(
                "MT5 must not receive an invalid order request"
            )

    executor = MT5BrokerExecutor(
        FakeMT5Client(),
        volume=0,
    )

    result = executor.execute(plan)

    assert result.status == ExecutionStatus.REJECTED
    assert result.message == "Volume must be positive"

def test_mt5_broker_executor_uses_configured_volume():
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

    class FakeMT5Client:
        def __init__(self):
            self.received_request = None

        def send_order(self, request):
            self.received_request = request
            return True

    client = FakeMT5Client()
    executor = MT5BrokerExecutor(
        client,
        volume=2.5,
    )

    result = executor.execute(plan)

    assert result.status == ExecutionStatus.EXECUTED
    assert client.received_request["volume"] == 2.5

def test_mt5_broker_executor_rejects_invalid_trade_plan():
    plan = TradePlan(
        symbol="NAS100",
        timeframe=1,
        direction=TradeDirection.BUY,
        entry_price=29442.3,
        stop_loss=29445.0,
        take_profit=29446.9,
        risk_distance=2.3,
        orderblock_index=21,
    )

    class FakeMT5Client:
        def send_order(self, request):
            raise AssertionError(
                "MT5 must not receive an invalid trade request"
            )

    executor = MT5BrokerExecutor(
        FakeMT5Client(),
        volume=2.0,
    )

    result = executor.execute(plan)

    assert result.status == ExecutionStatus.REJECTED
    assert result.message == "Invalid BUY trade levels"

def test_mt5_broker_executor_rejects_when_mt5_raises():
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

    class FakeMT5Client:
        def send_order(self, request):
            raise RuntimeError("MT5 connection failed")

    executor = MT5BrokerExecutor(
        FakeMT5Client(),
        volume=1.0,
    )

    result = executor.execute(plan)

    assert result.status == ExecutionStatus.REJECTED
    assert result.message == "MT5 connection failed"

def test_mt5_broker_executor_preserves_client_result():
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

    class FakeMT5Client:
        def send_order(self, request):
            return {
                "retcode": 10009,
                "order": 123456,
            }

    executor = MT5BrokerExecutor(
        FakeMT5Client(),
        volume=1.0,
    )

    result = executor.execute(plan)

    assert result.status == ExecutionStatus.EXECUTED
    assert result.message == "MT5 order executed"
    assert result.broker_result == {
        "retcode": 10009,
        "order": 123456,
    }

def test_mt5_broker_executor_rejects_broker_result_with_failed_retcode():
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

    class FakeMT5Client:
        def send_order(self, request):
            return {
                "retcode": 10006,
                "comment": "Request rejected",
            }

    executor = MT5BrokerExecutor(
        FakeMT5Client(),
        volume=1.0,
    )

    result = executor.execute(plan)

    assert result.status == ExecutionStatus.REJECTED
    assert result.message == "Request rejected"
    assert result.broker_result == {
        "retcode": 10006,
        "comment": "Request rejected",
    }

def test_mt5_broker_executor_accepts_configured_success_retcode():
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

    class FakeMT5Client:
        def send_order(self, request):
            return {
                "retcode": 20000,
                "order": 123456,
            }

    executor = MT5BrokerExecutor(
        FakeMT5Client(),
        volume=1.0,
        success_retcode=20000,
    )

    result = executor.execute(plan)

    assert result.status == ExecutionStatus.EXECUTED
    assert result.broker_result == {
        "retcode": 20000,
        "order": 123456,
    }

def test_mt5_broker_executor_rejects_non_positive_success_retcode():
    class FakeMT5Client:
        pass

    with pytest.raises(
        ValueError,
        match="Success retcode must be positive",
    ):
        MT5BrokerExecutor(
            FakeMT5Client(),
            success_retcode=0,
        )
