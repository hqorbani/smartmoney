from smartmoney.analyzers.position_size import PositionSizeAnalyzer
from smartmoney.core.context import MarketContext
from smartmoney.models.position_size import PositionSizePlan
from smartmoney.models.signal import SignalDirection
from smartmoney.models.symbol_trading_info import SymbolTradingInfo
from types import SimpleNamespace

def make_context(
    direction,
    entry_price,
    stop_loss,
    take_profit,
):
    context = MarketContext(
        symbol="TEST",
        timeframe=15,
        df=None,
    )

    context.trade_plan = SimpleNamespace(
        direction=direction,
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
    )

    context.position_size_plan = None

    return context


def make_analyzer(
    balance,
    risk_percent,
    tick_size=1.0,
    tick_value=1.0,
):
    return PositionSizeAnalyzer(
        balance=balance,
        risk_percent=risk_percent,
        symbol_trading_info_provider=lambda symbol: SymbolTradingInfo(
            tick_size=tick_size,
            tick_value=tick_value,
            contract_size=1.0,
            digits=2,
            volume_min=0.01,
            volume_max=100.0,
            volume_step=0.01,
        ),
    )


def test_bullish_position_size_is_calculated():
    context = make_context(
        direction=SignalDirection.BUY,
        entry_price=100,
        stop_loss=98,
        take_profit=104,
    )

    make_analyzer(
        balance=10_000,
        risk_percent=1.0,
    ).analyze(context)

    assert context.position_size_plan is not None

    plan = context.position_size_plan

    assert plan.balance == 10_000
    assert plan.risk_percent == 1.0
    assert plan.risk_amount == 100
    assert plan.stop_distance == 2
    assert plan.position_size == 50


def test_bearish_position_size_is_calculated():
    context = make_context(
        direction=SignalDirection.SELL,
        entry_price=100,
        stop_loss=102,
        take_profit=96,
    )

    make_analyzer(
        balance=10_000,
        risk_percent=1.0,
    ).analyze(context)

    assert context.position_size_plan is not None

    plan = context.position_size_plan

    assert plan.balance == 10_000
    assert plan.risk_percent == 1.0
    assert plan.risk_amount == 100
    assert plan.stop_distance == 2
    assert plan.position_size == 50


def test_position_size_changes_with_risk_percent():
    context = make_context(
        direction=SignalDirection.BUY,
        entry_price=100,
        stop_loss=95,
        take_profit=110,
    )

    make_analyzer(
        balance=20_000,
        risk_percent=2.0,
    ).analyze(context)

    assert context.position_size_plan is not None

    plan = context.position_size_plan

    assert plan.balance == 20_000
    assert plan.risk_percent == 2.0
    assert plan.risk_amount == 400
    assert plan.stop_distance == 5
    assert plan.position_size == 80


def test_no_position_size_without_tradeplan():
    context = MarketContext(
        symbol="TEST",
        timeframe=15,
        df=None,
    )

    context.trade_plan = None
    context.position_size_plan = None

    make_analyzer(
        balance=10_000,
        risk_percent=1.0,
    ).analyze(context)

    assert context.position_size_plan is None


def test_no_position_size_when_stop_distance_is_zero():
    context = make_context(
        direction=SignalDirection.BUY,
        entry_price=100,
        stop_loss=100,
        take_profit=110,
    )

    make_analyzer(
        balance=10_000,
        risk_percent=1.0,
    ).analyze(context)

    assert context.position_size_plan is None


def test_no_position_size_when_balance_is_zero():
    context = make_context(
        direction=SignalDirection.BUY,
        entry_price=100,
        stop_loss=98,
        take_profit=104,
    )

    make_analyzer(
        balance=0,
        risk_percent=1.0,
    ).analyze(context)

    assert context.position_size_plan is None


def test_no_position_size_when_balance_is_negative():
    context = make_context(
        direction=SignalDirection.BUY,
        entry_price=100,
        stop_loss=98,
        take_profit=104,
    )

    make_analyzer(
        balance=-10_000,
        risk_percent=1.0,
    ).analyze(context)

    assert context.position_size_plan is None


def test_no_position_size_when_risk_percent_is_zero():
    context = make_context(
        direction=SignalDirection.BUY,
        entry_price=100,
        stop_loss=98,
        take_profit=104,
    )

    make_analyzer(
        balance=10_000,
        risk_percent=0,
    ).analyze(context)

    assert context.position_size_plan is None


def test_no_position_size_when_risk_percent_is_above_100():
    context = make_context(
        direction=SignalDirection.BUY,
        entry_price=100,
        stop_loss=98,
        take_profit=104,
    )

    make_analyzer(
        balance=10_000,
        risk_percent=101.0,
    ).analyze(context)

    assert context.position_size_plan is None


def test_position_size_model_stores_calculated_values():
    plan = PositionSizePlan(
        balance=10_000,
        risk_percent=1.0,
        risk_amount=100,
        stop_distance=2,
        position_size=50,
    )

    assert plan.balance == 10_000
    assert plan.risk_percent == 1.0
    assert plan.risk_amount == 100
    assert plan.stop_distance == 2
    assert plan.position_size == 50
