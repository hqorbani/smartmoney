import pandas as pd

from smartmoney.analyzers.entry import EntryAnalyzer
from smartmoney.analyzers.fvg import FVGAnalyzer
from smartmoney.analyzers.orderblock import OrderBlockAnalyzer
from smartmoney.analyzers.position_size import PositionSizeAnalyzer
from smartmoney.analyzers.signal import SignalAnalyzer
from smartmoney.analyzers.stoploss import StopLossAnalyzer
from smartmoney.analyzers.takeprofit import TakeProfitAnalyzer
from smartmoney.analyzers.tradeplan import TradePlanAnalyzer
from smartmoney.core.context import MarketContext
from smartmoney.core.engine import AnalyzerEngine
from smartmoney.models.signal import SignalDirection


def make_context(rows):
    df = pd.DataFrame(rows)
    df["time"] = pd.to_datetime(df["time"])

    return MarketContext(
        symbol="TEST",
        timeframe=15,
        df=df,
    )


def make_engine():
    engine = AnalyzerEngine()

    engine.add(FVGAnalyzer())
    engine.add(OrderBlockAnalyzer())
    engine.add(SignalAnalyzer())
    engine.add(EntryAnalyzer())
    engine.add(StopLossAnalyzer())
    engine.add(TakeProfitAnalyzer())
    engine.add(TradePlanAnalyzer())
    engine.add(
        PositionSizeAnalyzer(
            balance=10_000,
            risk_percent=1.0,
        )
    )

    return engine


def test_full_bullish_pipeline_creates_position_size():

    context = make_context([
        {
            "time": "2026-01-01 10:00",
            "open": 101,
            "high": 103,
            "low": 98,
            "close": 99,
        },
        {
            "time": "2026-01-01 10:15",
            "open": 99,
            "high": 108,
            "low": 99,
            "close": 107,
        },
        {
            "time": "2026-01-01 10:30",
            "open": 107,
            "high": 112,
            "low": 105,
            "close": 110,
        },
        {
            "time": "2026-01-01 10:45",
            "open": 110,
            "high": 111,
            "low": 99,
            "close": 100,
        },
    ])

    make_engine().run(context)

    assert context.signal.direction == SignalDirection.BUY
    assert context.entry_plan is not None
    assert context.stop_loss_plan is not None
    assert context.take_profit_plan is not None
    assert context.trade_plan is not None
    assert context.position_size_plan is not None

    trade = context.trade_plan
    position = context.position_size_plan

    assert trade.direction == SignalDirection.BUY
    assert trade.entry_price == context.entry_plan.entry_price
    assert trade.stop_loss == context.stop_loss_plan.stop_loss
    assert trade.take_profit == context.take_profit_plan.take_profit

    assert trade.risk > 0
    assert trade.reward > 0
    assert trade.risk_reward_ratio == 2.0

    assert position.balance == 10_000
    assert position.risk_percent == 1.0
    assert position.risk_amount == 100
    assert position.stop_distance == trade.risk
    assert position.position_size == 100 / trade.risk


def test_full_bearish_pipeline_creates_position_size():

    context = make_context([
        {
            "time": "2026-01-01 10:00",
            "open": 99,
            "high": 103,
            "low": 98,
            "close": 102,
        },
        {
            "time": "2026-01-01 10:15",
            "open": 102,
            "high": 102,
            "low": 93,
            "close": 94,
        },
        {
            "time": "2026-01-01 10:30",
            "open": 94,
            "high": 96,
            "low": 90,
            "close": 91,
        },
        {
            "time": "2026-01-01 10:45",
            "open": 91,
            "high": 102,
            "low": 90,
            "close": 101,
        },
    ])

    make_engine().run(context)

    assert context.signal.direction == SignalDirection.SELL
    assert context.entry_plan is not None
    assert context.stop_loss_plan is not None
    assert context.take_profit_plan is not None
    assert context.trade_plan is not None
    assert context.position_size_plan is not None

    trade = context.trade_plan
    position = context.position_size_plan

    assert trade.direction == SignalDirection.SELL
    assert trade.entry_price == context.entry_plan.entry_price
    assert trade.stop_loss == context.stop_loss_plan.stop_loss
    assert trade.take_profit == context.take_profit_plan.take_profit

    assert trade.risk > 0
    assert trade.reward > 0
    assert trade.risk_reward_ratio == 2.0

    assert position.balance == 10_000
    assert position.risk_percent == 1.0
    assert position.risk_amount == 100
    assert position.stop_distance == trade.risk
    assert position.position_size == 100 / trade.risk

def test_engine_produces_same_signal_as_manual_pipeline():

    rows = [
        {
            "time": "2026-01-01 10:00",
            "open": 101,
            "high": 103,
            "low": 98,
            "close": 99,
        },
        {
            "time": "2026-01-01 10:15",
            "open": 99,
            "high": 108,
            "low": 99,
            "close": 107,
        },
        {
            "time": "2026-01-01 10:30",
            "open": 107,
            "high": 112,
            "low": 105,
            "close": 110,
        },
        {
            "time": "2026-01-01 10:45",
            "open": 110,
            "high": 111,
            "low": 99,
            "close": 100,
        },
    ]

    manual_context = make_context(rows)

    FVGAnalyzer().analyze(manual_context)
    OrderBlockAnalyzer().analyze(manual_context)
    SignalAnalyzer().analyze(manual_context)

    engine_context = make_context(rows)

    engine = AnalyzerEngine()
    engine.add(FVGAnalyzer())
    engine.add(OrderBlockAnalyzer())
    engine.add(SignalAnalyzer())

    engine.run(engine_context)

    assert engine_context.signal.direction == manual_context.signal.direction

def test_full_engine_keeps_signal_after_each_pipeline_stage():

    rows = [
        {
            "time": "2026-01-01 10:00",
            "open": 101,
            "high": 103,
            "low": 98,
            "close": 99,
        },
        {
            "time": "2026-01-01 10:15",
            "open": 99,
            "high": 108,
            "low": 99,
            "close": 107,
        },
        {
            "time": "2026-01-01 10:30",
            "open": 107,
            "high": 112,
            "low": 105,
            "close": 110,
        },
        {
            "time": "2026-01-01 10:45",
            "open": 110,
            "high": 111,
            "low": 99,
            "close": 100,
        },
    ]

    context = make_context(rows)

    analyzers = [
        FVGAnalyzer(),
        OrderBlockAnalyzer(),
        SignalAnalyzer(),
        EntryAnalyzer(),
        StopLossAnalyzer(),
        TakeProfitAnalyzer(),
        TradePlanAnalyzer(),
        PositionSizeAnalyzer(
            balance=10_000,
            risk_percent=1.0,
        ),
    ]

    for analyzer in sorted(analyzers, key=lambda item: item.priority):
        analyzer.analyze(context)

        print(
            f"{analyzer.__class__.__name__}: "
            f"priority={analyzer.priority}, "
            f"signal={context.signal.direction}, "
            f"fvgs={len(context.fvgs)}, "
            f"orderblocks={len(context.orderblocks)}, "
            f"entry={context.entry_plan}, "
            f"stop_loss={context.stop_loss_plan}, "
            f"take_profit={context.take_profit_plan}, "
            f"trade_plan={context.trade_plan}, "
            f"position_size={context.position_size_plan}"
        )

    assert context.signal.direction == SignalDirection.BUY

def test_signal_and_entry_are_created_when_price_enters_orderblock():

    context = make_context([
        {
            "time": "2026-01-01 10:00",
            "open": 101,
            "high": 103,
            "low": 98,
            "close": 99,
        },
        {
            "time": "2026-01-01 10:15",
            "open": 99,
            "high": 108,
            "low": 99,
            "close": 107,
        },
        {
            "time": "2026-01-01 10:30",
            "open": 107,
            "high": 112,
            "low": 105,
            "close": 110,
        },
        {
            "time": "2026-01-01 10:45",
            "open": 110,
            "high": 111,
            "low": 99,
            "close": 100,
        },
    ])

    FVGAnalyzer().analyze(context)
    OrderBlockAnalyzer().analyze(context)

    assert len(context.fvgs) == 1
    assert len(context.orderblocks) == 1

    SignalAnalyzer().analyze(context)

    assert context.signal.direction == SignalDirection.BUY

    EntryAnalyzer().analyze(context)

    assert context.entry_plan is not None
    assert context.entry_plan.entry_price == (
        context.orderblocks[0].high
        + context.orderblocks[0].low
    ) / 2.0    