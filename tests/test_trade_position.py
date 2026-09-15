import pytest
from smartmoney.trading.trade_plan import TradeDirection, TradePlan
from smartmoney.trading.trade_position import (
    ExitReason,
    PositionStatus,
    TradePosition,
)

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

    closed_position = position.close(
    exit_price=29446.2,
    exit_reason=ExitReason.TAKE_PROFIT,
)

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

    closed_position = position.close(
    exit_price=29446.2,
    exit_reason=ExitReason.TAKE_PROFIT,
)

    with pytest.raises(
        ValueError,
        match="Trade position is already closed",
    ):
        closed_position.close(
            exit_price=29446.2,
            exit_reason=ExitReason.TAKE_PROFIT,
        )

def test_closed_trade_position_stores_exit_price():
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

    closed_position = position.close(
    exit_price=29446.2,
    exit_reason=ExitReason.TAKE_PROFIT,
)

    assert closed_position.status == PositionStatus.CLOSED
    assert closed_position.plan == position.plan
    assert closed_position.size == position.size
    assert closed_position.exit_price == 29446.2

def test_closed_trade_position_stores_exit_reason():
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

    closed_position = position.close(
        exit_price=29446.2,
        exit_reason=ExitReason.TAKE_PROFIT,
    )

    assert closed_position.status == PositionStatus.CLOSED
    assert closed_position.exit_price == 29446.2
    assert closed_position.exit_reason == ExitReason.TAKE_PROFIT

def test_trade_position_cannot_be_closed_without_exit_reason():
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

    with pytest.raises(
        ValueError,
        match="Exit reason must not be empty",
    ):
        position.close(
            exit_price=29446.2,
            exit_reason="",
        )

def test_trade_position_uses_exit_reason_enum():
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

    closed_position = position.close(
        exit_price=29446.2,
        exit_reason=ExitReason.TAKE_PROFIT,
    )

    assert closed_position.exit_reason == ExitReason.TAKE_PROFIT     

def test_trade_position_rejects_string_exit_reason():
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

    with pytest.raises(
        ValueError,
        match="Invalid exit reason",
    ):
        position.close(
            exit_price=29446.2,
            exit_reason="TAKE_PROFIT",
        )       