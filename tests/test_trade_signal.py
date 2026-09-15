import pandas as pd

from smartmoney.backtesting.orderblock_zones import (
    OrderBlockDepthZone,
)
from smartmoney.execution.signal import (
    TradeDirection,
    TradeSignal,
)
from smartmoney.models.orderblock import OrderBlock


def test_trade_signal_stores_trade_data():
    orderblock = OrderBlock(
        index=10,
        time=pd.Timestamp("2026-01-01 10:00:00"),
        open=100.0,
        high=105.0,
        low=99.0,
        close=104.0,
        bullish=True,
    )

    signal = TradeSignal(
        symbol="NAS100",
        timeframe=3,
        direction=TradeDirection.BUY,
        orderblock=orderblock,
        touch_zone=OrderBlockDepthZone.FIRST,
        entry_price=103.0,
        stop_loss=99.0,
        take_profit=111.0,
        risk=4.0,
        reward=8.0,
        rr=2.0,
    )

    assert signal.symbol == "NAS100"
    assert signal.timeframe == 3

    assert signal.direction is TradeDirection.BUY

    assert signal.orderblock is orderblock
    assert signal.touch_zone is OrderBlockDepthZone.FIRST

    assert signal.entry_price == 103.0
    assert signal.stop_loss == 99.0
    assert signal.take_profit == 111.0

    assert signal.risk == 4.0
    assert signal.reward == 8.0
    assert signal.rr == 2.0