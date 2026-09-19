from apps.demo_order import execute_demo_order


from apps.demo_order import execute_demo_order
from smartmoney.trading.trade_plan import TradeDirection


def test_execute_demo_order_uses_requested_trade():
    class FakeExecutor:
        def __init__(self):
            self.plan = None
            self.volume = None

        def initialize(self):
            return True

        def execute(self, plan):
            self.plan = plan
            return type(
                "Result",
                (),
                {"status": "executed"},
            )()

        def shutdown(self):
            return True

    executor = FakeExecutor()

    result = execute_demo_order(
        executor=executor,
        symbol="ETHEREUM",
        direction="BUY",
        volume=0.01,
        stop_loss=2625,
        take_profit=2656,
    )

    assert result.status == "executed"
    assert executor.volume == 0.01
    assert executor.plan.symbol == "ETHEREUM"
    assert executor.plan.direction == TradeDirection.BUY
    assert executor.plan.stop_loss == 2625
    assert executor.plan.take_profit == 2656