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

def test_build_real_mt5_buy_order_request():
    from smartmoney.trading.mt5_order_request import (
        build_real_mt5_order_request,
    )
    from smartmoney.trading.trade_plan import (
        TradeDirection,
        TradePlan,
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

    request = build_real_mt5_order_request(
        plan=plan,
        volume=0.01,
        price=1.15411,
        deviation=20,
        magic=234000,
        comment="smartmoney test",
        type_filling=2,
    )

    assert request["symbol"] == "EURUSD"
    assert request["volume"] == 0.01
    assert request["type"] >= 0
    assert request["action"] > 0
    assert request["price"] == 1.15411
    assert request["sl"] == 1.15300
    assert request["tp"] == 1.15600
    assert request["deviation"] == 20
    assert request["magic"] == 234000
    assert request["comment"] == "smartmoney test"
    assert request["type_time"] >= 0
    assert request["type_filling"] == 2

def test_build_real_mt5_sell_order_request():
    from smartmoney.trading.mt5_order_request import (
        build_real_mt5_order_request,
    )
    from smartmoney.trading.trade_plan import (
        TradeDirection,
        TradePlan,
    )

    plan = TradePlan(
        symbol="EURUSD",
        timeframe=15,
        direction=TradeDirection.SELL,
        entry_price=1.15400,
        stop_loss=1.15500,
        take_profit=1.15200,
        risk_distance=0.00100,
        orderblock_index=10,
    )

    request = build_real_mt5_order_request(
        plan=plan,
        volume=0.01,
        price=1.15400,
        deviation=20,
        magic=234000,
        comment="smartmoney sell test",
        type_filling=2,
    )

    assert request["symbol"] == "EURUSD"
    assert request["volume"] == 0.01
    assert request["type"] == 1
    assert request["action"] > 0
    assert request["price"] == 1.15400
    assert request["sl"] == 1.15500
    assert request["tp"] == 1.15200
    assert request["deviation"] == 20
    assert request["magic"] == 234000
    assert request["comment"] == "smartmoney sell test"
    assert request["type_time"] >= 0
    assert request["type_filling"] == 2

def test_build_real_mt5_order_request_uses_configured_filling_mode():
    from smartmoney.trading.mt5_order_request import (
        build_real_mt5_order_request,
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

    request = build_real_mt5_order_request(
        plan=plan,
        volume=0.01,
        price=1.15420,
        deviation=20,
        magic=234000,
        comment="smartmoney test",
        type_filling=1,
    )

    assert request["type_filling"] == 1