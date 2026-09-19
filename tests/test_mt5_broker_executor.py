from smartmoney.trading.execution import ExecutionResult, ExecutionStatus
from smartmoney.trading.mt5_broker_executor import MT5BrokerExecutor
from smartmoney.trading.trade_plan import TradeDirection, TradePlan
import pytest
from smartmoney.trading.trade_plan import (
    TradeDirection,
    TradePlan,
)
import MetaTrader5 as mt5

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
        def order_check(self, request):
            return {
                "retcode": 10009,
                "comment": "Done",
            }
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

        def order_check(self, request):
            return {
                "retcode": 10009,
                "comment": "Done",
            }

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
        def order_check(self, request):
            return {
                "retcode": 10009,
                "comment": "Done",
            }

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

        def order_check(self, request):
            return {
                "retcode": 10009,
                "comment": "Done",
            }

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

        def order_check(self, request):
            return {
                "retcode": 10009,
                "comment": "Done",
            }

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
        def order_check(self, request):
            return {
                "retcode": 10009,
                "comment": "Done",
            }

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
        def order_check(self, request):
            return {
                "retcode": 10009,
                "comment": "Done",
            }

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
        def order_check(self, request):
            return {
                "retcode": 10009,
                "comment": "Done",
            }
    
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
        def order_check(self, request):
            return {
                "retcode": 10009,
                "comment": "Done",
            }

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

def test_mt5_broker_executor_initializes_mt5_client():
    from smartmoney.trading.mt5_broker_executor import MT5BrokerExecutor

    class FakeMT5Client:
        def __init__(self):
            self.initialized = False

        def initialize(self):
            self.initialized = True
            return True

    client = FakeMT5Client()

    executor = MT5BrokerExecutor(client)

    assert executor.initialize() is True
    assert client.initialized is True

def test_mt5_broker_executor_returns_false_when_initialization_fails():
    from smartmoney.trading.mt5_broker_executor import MT5BrokerExecutor

    class FakeMT5Client:
        def initialize(self):
            return False

    executor = MT5BrokerExecutor(
        FakeMT5Client(),
    )

    assert executor.initialize() is False

def test_mt5_broker_executor_shuts_down_mt5_client():
    from smartmoney.trading.mt5_broker_executor import MT5BrokerExecutor

    class FakeMT5Client:
        def __init__(self):
            self.shutdown_called = False

        def shutdown(self):
            self.shutdown_called = True
            return True

    client = FakeMT5Client()

    executor = MT5BrokerExecutor(client)

    assert executor.shutdown() is True
    assert client.shutdown_called is True

def test_mt5_broker_executor_uses_client_send_order():
    from smartmoney.trading.mt5_broker_executor import MT5BrokerExecutor
    from smartmoney.trading.execution import ExecutionStatus

    class FakeMT5Client:
        def __init__(self):
            self.requests = []

        def order_check(self, request):
            return {
                "retcode": 10009,
                "comment": "Done",
            }

        def send_order(self, request):
            self.requests.append(request)
            return {
                "retcode": 10009,
                "comment": "done",
            }

    client = FakeMT5Client()

    executor = MT5BrokerExecutor(
        client,
    )

    plan = TradePlan(
        symbol="EURUSD",
        timeframe=15,
        direction=TradeDirection.BUY,
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit=1.1100,
        risk_distance=0.0050,
        orderblock_index=10,
    )

    result = executor.execute(plan)

    assert result.status == ExecutionStatus.EXECUTED
    assert len(client.requests) == 1

def test_mt5_broker_executor_can_use_mt5_client():
    from smartmoney.trading.mt5_broker_executor import MT5BrokerExecutor
    from smartmoney.trading.mt5_client import MT5Client

    client = MT5Client()
    executor = MT5BrokerExecutor(client)

    assert executor.mt5_client is client

def test_executor_builds_real_mt5_request():
    from smartmoney.trading.mt5_broker_executor import (
        MT5BrokerExecutor,
    )
    from smartmoney.trading.trade_plan import (
        TradeDirection,
        TradePlan,
    )

    class FakeMT5Client:

        def __init__(self):
            self.received_request = None
        def symbol_info(self, symbol):
            return type("SymbolInfo", (), {"filling_mode": 1})()
        def market_price(self, symbol):
            return {
                "bid": 1.15400,
                "ask": 1.15420,
            }

        def order_check(self, request):
            return {
                "retcode": 10009,
                "comment": "Done",
            }
        
        def send_order(self, request):
            self.received_request = request
            return True

    client = FakeMT5Client()

    executor = MT5BrokerExecutor(
        mt5_client=client,
        volume=0.01,
        use_real_request=True,
    )

    plan = TradePlan(
        symbol="EURUSD",
        timeframe=15,
        direction=TradeDirection.BUY,
        entry_price=1.15411,
        stop_loss=1.15300,
        take_profit=1.15600,
        risk_distance=0.00111,
        orderblock_index=10,
    )

    result = executor.execute(plan)

    assert result.status.value == "executed"
    assert client.received_request is not None
    assert client.received_request["action"] > 0
    assert client.received_request["symbol"] == "EURUSD"
    assert client.received_request["volume"] == 0.01
    assert client.received_request["price"] == 1.15420
    assert client.received_request["sl"] == 1.15300
    assert client.received_request["tp"] == 1.15600

def test_executor_uses_market_price_for_real_request():
    from smartmoney.trading.mt5_broker_executor import (
        MT5BrokerExecutor,
    )
    from smartmoney.trading.trade_plan import (
        TradeDirection,
        TradePlan,
    )

    class FakeMT5Client:
        def __init__(self):
            self.received_request = None
        def symbol_info(self, symbol):
            return type("SymbolInfo", (), {"filling_mode": 1})()
        def market_price(self, symbol):
            assert symbol == "EURUSD"

            return {
                "bid": 1.15400,
                "ask": 1.15420,
            }
        def order_check(self, request):
            return {
                "retcode": 10009,
                "comment": "Done",
            }
        
        def send_order(self, request):
            self.received_request = request
            return True

    client = FakeMT5Client()

    executor = MT5BrokerExecutor(
        mt5_client=client,
        volume=0.01,
        use_real_request=True,
    )

    plan = TradePlan(
        symbol="EURUSD",
        timeframe=15,
        direction=TradeDirection.BUY,
        entry_price=1.15411,
        stop_loss=1.15300,
        take_profit=1.15600,
        risk_distance=0.00111,
        orderblock_index=10,
    )

    result = executor.execute(plan)

    assert result.status.value == "executed"
    assert client.received_request is not None
    assert client.received_request["price"] == 1.15420

def test_executor_uses_bid_price_for_real_sell_request():
    class FakeMT5Client:
        def __init__(self):
            self.received_request = None
        def symbol_info(self, symbol):
            return type("SymbolInfo", (), {"filling_mode": 1})()
        def market_price(self, symbol):
            return {
                "bid": 1.15400,
                "ask": 1.15420,
            }
        def order_check(self, request):
            return {
                "retcode": 10009,
                "comment": "Done",
            }
        
        def send_order(self, request):
            self.received_request = request
            return {
                "retcode": 10009,
                "comment": "Done",
            }

    client = FakeMT5Client()

    executor = MT5BrokerExecutor(
        mt5_client=client,
        volume=1.0,
        use_real_request=True,
    )

    plan = TradePlan(
        symbol="EURUSD",
        timeframe=15,
        direction=TradeDirection.SELL,
        entry_price=1.15400,
        stop_loss=1.15500,
        take_profit=1.15300,
        risk_distance=0.00100,
        orderblock_index=10,
    )

    result = executor.execute(plan)

    assert result.status == ExecutionStatus.EXECUTED
    assert client.received_request["price"] == 1.15400
    assert client.received_request["type"] == mt5.ORDER_TYPE_SELL

def test_executor_rejects_when_order_check_fails_without_sending():
    class FakeMT5Client:
        def __init__(self):
            self.order_check_called = False
            self.send_order_called = False
        def symbol_info(self, symbol):
            return type("SymbolInfo", (), {"filling_mode": 1})()
        def market_price(self, symbol):
            return {
                "bid": 1.15400,
                "ask": 1.15420,
            }

        def order_check(self, request):
            self.order_check_called = True
            return {
                "retcode": 10016,
                "comment": "Invalid stops",
            }

        def send_order(self, request):
            self.send_order_called = True
            raise AssertionError(
                "order_send must not be called when order_check fails"
            )

    client = FakeMT5Client()

    executor = MT5BrokerExecutor(
        mt5_client=client,
        volume=0.01,
        use_real_request=True,
    )

    plan = TradePlan(
        symbol="EURUSD",
        timeframe=15,
        direction=TradeDirection.BUY,
        entry_price=1.15411,
        stop_loss=1.15300,
        take_profit=1.15600,
        risk_distance=0.00111,
        orderblock_index=10,
    )

    result = executor.execute(plan)

    assert client.order_check_called is True
    assert client.send_order_called is False
    assert result.status == ExecutionStatus.REJECTED
    assert result.message == "Invalid stops"

def test_executor_sends_order_when_order_check_succeeds():
    class FakeMT5Client:
        def __init__(self):
            self.order_check_called = False
            self.send_order_called = False
        def symbol_info(self, symbol):
            return type("SymbolInfo", (), {"filling_mode": 1})()
        def market_price(self, symbol):
            return {
                "bid": 1.15400,
                "ask": 1.15420,
            }

        def order_check(self, request):
            self.order_check_called = True
            return {
                "retcode": 10009,
                "comment": "Done",
            }

        def send_order(self, request):
            self.send_order_called = True
            return {
                "retcode": 10009,
                "comment": "Done",
                "order": 123456,
            }

    client = FakeMT5Client()

    executor = MT5BrokerExecutor(
        mt5_client=client,
        volume=0.01,
        use_real_request=True,
    )

    plan = TradePlan(
        symbol="EURUSD",
        timeframe=15,
        direction=TradeDirection.BUY,
        entry_price=1.15411,
        stop_loss=1.15300,
        take_profit=1.15600,
        risk_distance=0.00111,
        orderblock_index=10,
    )

    result = executor.execute(plan)

    assert client.order_check_called is True
    assert client.send_order_called is True
    assert result.status == ExecutionStatus.EXECUTED

def test_executor_uses_symbol_filling_mode():
    from smartmoney.trading.mt5_broker_executor import MT5BrokerExecutor

    class FakeMT5Client:
        def __init__(self):
            self.sent_request = None

        def symbol_info(self, symbol):
            return type("SymbolInfo", (), {"filling_mode": 1})()

        def market_price(self, symbol):
            return {"ask": 1.15420, "bid": 1.15400}

        def order_check(self, request):
            return {"retcode": 10009, "comment": "Done"}

        def send_order(self, request):
            self.sent_request = request
            return {"retcode": 10009, "order": 123}

    plan = TradePlan(
        symbol="EURUSD",
        timeframe=15,
        direction=TradeDirection.BUY,
        entry_price=1.15411,
        stop_loss=1.15300,
        take_profit=1.15600,
        risk_distance=0.00111,
        orderblock_index=10,
    )

    client = FakeMT5Client()
    executor = MT5BrokerExecutor(
        mt5_client=client,
        use_real_request=True,
    )

    result = executor.execute(plan)
    print(result)

    assert client.sent_request["type_filling"] == 1    