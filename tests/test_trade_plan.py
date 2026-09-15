from smartmoney.trading.trade_plan import (
    TradeDirection,
    TradePlan,
)


def test_trade_plan_stores_trade_information():
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

    assert plan.symbol == "NAS100"
    assert plan.timeframe == 1
    assert plan.direction == TradeDirection.BUY
    assert plan.entry_price == 29442.3
    assert plan.stop_loss == 29440.0
    assert plan.take_profit == 29446.9
    assert plan.risk_distance == 2.3
    assert plan.orderblock_index == 21