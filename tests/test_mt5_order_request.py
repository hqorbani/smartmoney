import pytest
from smartmoney.trading.mt5_order_request import (
    build_mt5_order_request,
)
from smartmoney.trading.trade_plan import (
    TradeDirection,
    TradePlan,
)


def test_build_mt5_buy_order_request():
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

    request = build_mt5_order_request(
        plan=plan,
        volume=2.0,
    )

    assert request["symbol"] == "NAS100"
    assert request["volume"] == 2.0
    assert request["entry_price"] == 29442.3
    assert request["stop_loss"] == 29440.0
    assert request["take_profit"] == 29446.9

def test_build_mt5_order_request_rejects_non_positive_volume():
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

    with pytest.raises(
        ValueError,
        match="Volume must be positive",
    ):
        build_mt5_order_request(
            plan=plan,
            volume=0,
        )

def test_build_mt5_sell_order_request_contains_sell_direction():
    plan = TradePlan(
        symbol="NAS100",
        timeframe=1,
        direction=TradeDirection.SELL,
        entry_price=29442.3,
        stop_loss=29444.6,
        take_profit=29437.7,
        risk_distance=2.3,
        orderblock_index=21,
    )

    request = build_mt5_order_request(
        plan=plan,
        volume=2.0,
    )

    assert request["direction"] == "sell"

def test_build_mt5_order_request_rejects_invalid_direction():
    plan = TradePlan(
        symbol="NAS100",
        timeframe=1,
        direction="buy",
        entry_price=29442.3,
        stop_loss=29440.0,
        take_profit=29446.9,
        risk_distance=2.3,
        orderblock_index=21,
    )

    with pytest.raises(
        ValueError,
        match="Invalid trade direction",
    ):
        build_mt5_order_request(
            plan=plan,
            volume=2.0,
        )

def test_build_mt5_order_request_rejects_empty_symbol():
    plan = TradePlan(
        symbol="",
        timeframe=1,
        direction=TradeDirection.BUY,
        entry_price=29442.3,
        stop_loss=29440.0,
        take_profit=29446.9,
        risk_distance=2.3,
        orderblock_index=21,
    )

    with pytest.raises(
        ValueError,
        match="Symbol must not be empty",
    ):
        build_mt5_order_request(
            plan=plan,
            volume=2.0,
        )

def test_build_mt5_order_request_rejects_non_positive_timeframe():
    plan = TradePlan(
        symbol="NAS100",
        timeframe=0,
        direction=TradeDirection.BUY,
        entry_price=29442.3,
        stop_loss=29440.0,
        take_profit=29446.9,
        risk_distance=2.3,
        orderblock_index=21,
    )

    with pytest.raises(
        ValueError,
        match="Timeframe must be positive",
    ):
        build_mt5_order_request(
            plan=plan,
            volume=2.0,
        )

def test_build_mt5_order_request_rejects_non_positive_risk():
    plan = TradePlan(
        symbol="NAS100",
        timeframe=1,
        direction=TradeDirection.BUY,
        entry_price=29442.3,
        stop_loss=29440.0,
        take_profit=29446.9,
        risk_distance=0,
        orderblock_index=21,
    )

    with pytest.raises(
        ValueError,
        match="Trade plan risk must be positive",
    ):
        build_mt5_order_request(
            plan=plan,
            volume=2.0,
        )

def test_build_mt5_order_request_rejects_invalid_buy_levels():
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

    with pytest.raises(
        ValueError,
        match="Invalid BUY trade levels",
    ):
        build_mt5_order_request(
            plan=plan,
            volume=2.0,
        )

def test_build_mt5_order_request_rejects_invalid_sell_levels():
    plan = TradePlan(
        symbol="NAS100",
        timeframe=1,
        direction=TradeDirection.SELL,
        entry_price=29442.3,
        stop_loss=29440.0,
        take_profit=29437.7,
        risk_distance=2.3,
        orderblock_index=21,
    )

    with pytest.raises(
        ValueError,
        match="Invalid SELL trade levels",
    ):
        build_mt5_order_request(
            plan=plan,
            volume=2.0,
        )

def test_build_mt5_sell_order_request_contains_all_values():
    plan = TradePlan(
        symbol="NAS100",
        timeframe=1,
        direction=TradeDirection.SELL,
        entry_price=29442.3,
        stop_loss=29444.6,
        take_profit=29437.7,
        risk_distance=2.3,
        orderblock_index=21,
    )

    request = build_mt5_order_request(
        plan=plan,
        volume=2.0,
    )

    assert request == {
        "symbol": "NAS100",
        "volume": 2.0,
        "direction": "sell",
        "entry_price": 29442.3,
        "stop_loss": 29444.6,
        "take_profit": 29437.7,
    }                                                          