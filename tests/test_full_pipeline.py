import pandas as pd

from smartmoney.services.atr_service import ATRService
from smartmoney.models.symbol_trading_info import SymbolTradingInfo
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
import pytest

def make_context(rows):
    df = pd.DataFrame(rows)
    df["time"] = pd.to_datetime(df["time"])

    return MarketContext(
        symbol="EURUSD",
        timeframe=15,
        df=df,
    )


def make_position_size_analyzer():
    return PositionSizeAnalyzer(
        balance=10_000,
        risk_percent=1.0,
        symbol_trading_info_provider=lambda symbol: SymbolTradingInfo(
            tick_size=1.0,
            tick_value=1.0,
            contract_size=1.0,
            digits=2,
            volume_min=0.01,
            volume_max=100.0,
            volume_step=0.01,
        ),
        loss_per_lot_provider=lambda symbol, direction, entry_price, stop_loss: (
            abs(entry_price - stop_loss)
        ),
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
    engine.add(make_position_size_analyzer())

    return engine


def mock_atr(monkeypatch):
    monkeypatch.setattr(
        ATRService,
        "calculate",
        lambda self, df, period: pd.Series(
            4.0,
            index=df.index,
            dtype=float,
        ),
    )


def bullish_rows():
    return [
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


def bearish_rows():
    return [
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
    ]


def assert_position_size(context, expected_direction):
    assert context.signal.direction == expected_direction
    assert context.entry_plan is not None
    assert context.stop_loss_plan is not None
    assert context.take_profit_plan is not None
    assert context.trade_plan is not None
    assert context.position_size_plan is not None

    trade = context.trade_plan
    position = context.position_size_plan

    assert trade.direction.value == expected_direction.value
    assert trade.entry_price == context.entry_plan.entry_price
    assert trade.stop_loss == context.stop_loss_plan.stop_loss
    assert trade.take_profit == context.take_profit_plan.take_profit

    assert trade.risk_distance > 0
    assert abs(trade.take_profit - trade.entry_price) > 0

    assert position.balance == 10_000
    assert position.risk_percent == 1.0
    assert position.risk_amount == 100
    assert position.stop_distance == trade.risk_distance
    assert position.position_size == pytest.approx(100 / trade.risk_distance, rel=1e-3)

def test_full_bullish_pipeline_creates_position_size(monkeypatch):
    mock_atr(monkeypatch)

    context = make_context(bullish_rows())
    make_engine().run(context)

    assert_position_size(context, SignalDirection.BUY)


def test_full_bearish_pipeline_creates_position_size(monkeypatch):
    mock_atr(monkeypatch)

    context = make_context(bearish_rows())
    make_engine().run(context)

    assert_position_size(context, SignalDirection.SELL)


def test_engine_produces_same_signal_as_manual_pipeline():
    rows = bullish_rows()

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


def test_full_engine_keeps_signal_after_each_pipeline_stage(monkeypatch):
    mock_atr(monkeypatch)

    context = make_context(bullish_rows())

    analyzers = [
        FVGAnalyzer(),
        OrderBlockAnalyzer(),
        SignalAnalyzer(),
        EntryAnalyzer(),
        StopLossAnalyzer(),
        TakeProfitAnalyzer(),
        TradePlanAnalyzer(),
        make_position_size_analyzer(),
    ]

    for analyzer in sorted(analyzers, key=lambda item: item.priority):
        analyzer.analyze(context)

    assert context.signal.direction == SignalDirection.BUY
    assert context.entry_plan is not None
    assert context.stop_loss_plan is not None
    assert context.take_profit_plan is not None
    assert context.trade_plan is not None
    assert context.position_size_plan is not None


def test_signal_and_entry_are_created_when_price_enters_orderblock(monkeypatch):
    mock_atr(monkeypatch)

    context = make_context(bullish_rows())

    FVGAnalyzer().analyze(context)
    OrderBlockAnalyzer().analyze(context)

    assert len(context.fvgs) == 1
    assert len(context.orderblocks) == 1

    SignalAnalyzer().analyze(context)

    assert context.signal.direction == SignalDirection.BUY

    EntryAnalyzer().analyze(context)

    assert context.entry_plan is not None
    assert context.entry_plan.entry_price == (
        context.orderblocks[0].expanded_high
    )
