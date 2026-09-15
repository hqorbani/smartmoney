import pytest
from smartmoney.trading.trade_plan import TradeDirection, TradePlan
from smartmoney.trading.trade_position import TradePosition
from smartmoney.trading.trade_position import PositionStatus


def test_trade_position_stores_open_trade_state():
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

    position = TradePosition(
        plan=plan,
        size=43.47826087,
    )

    assert position.plan == plan
    assert position.size == 43.47826087

def test_trade_position_starts_open():
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

    position = TradePosition(
        plan=plan,
        size=43.47826087,
    )

    assert position.status == PositionStatus.OPEN

def test_trade_position_can_be_closed():
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

    position = TradePosition(
        plan=plan,
        size=43.47826087,
    )

    closed_position = position.close()

    assert position.status == PositionStatus.OPEN
    assert closed_position.status == PositionStatus.CLOSED
    assert closed_position.plan == position.plan
    assert closed_position.size == position.size

def test_trade_position_can_be_created_from_execution_result():
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

    position = TradePosition(
        plan=plan,
        size=43.47826087,
    )

    assert position.status == PositionStatus.OPEN
    assert position.plan == plan
    assert position.size == 43.47826087

def test_closed_trade_position_cannot_be_closed_again():
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

    position = TradePosition(
        plan=plan,
        size=43.47826087,
    )

    closed_position = position.close()

    with pytest.raises(
        ValueError,
        match="Trade position is already closed",
    ):
        closed_position.close()    