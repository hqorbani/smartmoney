import pandas as pd

from smartmoney.models.orderblock import OrderBlock
from smartmoney.trading.planner import TradePlanner
from smartmoney.trading.trade_plan import TradeDirection
import pytest

def test_create_buy_trade_plan():
    ob = OrderBlock(
        index=21,
        time=pd.Timestamp("2026-09-10 03:42"),
        open=29442.0,
        high=29446.5,
        low=29440.0,
        close=29445.0,
        bullish=True,
    )

    planner = TradePlanner(
        symbol="NAS100",
        timeframe=1,
        rr=2.0,
    )

    plan = planner.create_plan(
        ob=ob,
        entry_price=29442.3,
    )

    assert plan.symbol == "NAS100"
    assert plan.timeframe == 1
    assert plan.direction == TradeDirection.BUY
    assert plan.entry_price == pytest.approx(29442.3)
    assert plan.stop_loss == pytest.approx(29440.0)
    assert plan.take_profit == pytest.approx(29446.9)
    assert plan.risk_distance == pytest.approx(2.3)
    assert plan.orderblock_index == 21


def test_create_sell_trade_plan():
    ob = OrderBlock(
        index=31,
        time=pd.Timestamp("2026-09-10 03:52"),
        open=29432.0,
        high=29434.5,
        low=29425.8,
        close=29428.0,
        bullish=False,
    )

    planner = TradePlanner(
        symbol="NAS100",
        timeframe=1,
        rr=2.0,
    )

    plan = planner.create_plan(
        ob=ob,
        entry_price=29427.0,
    )

    assert plan.direction == TradeDirection.SELL
    assert plan.entry_price == pytest.approx(29427.0)
    assert plan.stop_loss == pytest.approx(29434.5)
    assert plan.take_profit == pytest.approx(29412.0)
    assert plan.risk_distance == pytest.approx(7.5)

def test_planner_rejects_invalid_rr():
    with pytest.raises(ValueError, match="Risk-reward ratio must be positive"):
        TradePlanner(
            symbol="NAS100",
            timeframe=1,
            rr=0,
        )


def test_planner_rejects_empty_symbol():
    with pytest.raises(ValueError, match="Symbol must not be empty"):
        TradePlanner(
            symbol="",
            timeframe=1,
            rr=2.0,
        )

def test_planner_rejects_entry_outside_orderblock():
    ob = OrderBlock(
        index=21,
        time=pd.Timestamp("2026-09-10 03:42"),
        open=29442.0,
        high=29446.5,
        low=29440.0,
        close=29445.0,
        bullish=True,
    )

    planner = TradePlanner(
        symbol="NAS100",
        timeframe=1,
        rr=2.0,
    )

    with pytest.raises(
        ValueError,
        match="Entry price must be inside the Order Block",
    ):
        planner.create_plan(
            ob=ob,
            entry_price=29450.0,
        )        