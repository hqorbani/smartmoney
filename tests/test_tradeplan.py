from types import SimpleNamespace

from smartmoney.analyzers.tradeplan import TradePlanAnalyzer
from smartmoney.core.context import MarketContext
from smartmoney.models.signal import SignalDirection
from smartmoney.trading.trade_plan import TradeDirection


def make_context():
    context = MarketContext(
        symbol="TEST",
        timeframe=15,
        df=None,
    )

    context.trade_plan = None

    return context


def make_trade_context(
    direction,
    entry_price,
    stop_loss,
    take_profit,
):
    context = make_context()

    context.signal = SimpleNamespace(
        direction=direction,
    )

    context.entry_plan = SimpleNamespace(
        entry_price=entry_price,
    )

    context.stop_loss_plan = SimpleNamespace(
        entry_plan=context.entry_plan,
        stop_loss=stop_loss,
    )

    context.take_profit_plan = SimpleNamespace(
        stop_loss_plan=context.stop_loss_plan,
        take_profit=take_profit,
    )

    return context


def test_bullish_tradeplan_is_created():
    context = make_trade_context(
        direction=SignalDirection.BUY,
        entry_price=100,
        stop_loss=98,
        take_profit=104,
    )

    TradePlanAnalyzer().analyze(context)

    assert context.trade_plan is not None

    trade = context.trade_plan

    assert trade.direction == TradeDirection.BUY
    assert trade.entry_price == 100
    assert trade.stop_loss == 98
    assert trade.take_profit == 104
    assert trade.risk == 2
    assert trade.reward == 4
    assert trade.risk_reward_ratio == 2.0


def test_bearish_tradeplan_is_created():
    context = make_trade_context(
        direction=SignalDirection.SELL,
        entry_price=100,
        stop_loss=102,
        take_profit=96,
    )

    TradePlanAnalyzer().analyze(context)

    assert context.trade_plan is not None

    trade = context.trade_plan

    assert trade.direction == TradeDirection.SELL
    assert trade.entry_price == 100
    assert trade.stop_loss == 102
    assert trade.take_profit == 96
    assert trade.risk == 2
    assert trade.reward == 4
    assert trade.risk_reward_ratio == 2.0


def test_no_tradeplan_without_takeprofit():
    context = make_context()

    context.signal = SimpleNamespace(
        direction=SignalDirection.BUY,
    )

    context.entry_plan = SimpleNamespace(
        entry_price=100,
    )

    context.stop_loss_plan = SimpleNamespace(
        entry_plan=context.entry_plan,
        stop_loss=98,
    )

    context.take_profit_plan = None

    TradePlanAnalyzer().analyze(context)

    assert context.trade_plan is None