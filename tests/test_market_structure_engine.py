import pandas as pd

from smartmoney.core.context import MarketContext
from smartmoney.core.market_structure_engine import MarketStructureEngine
from smartmoney.models.market_structure import MarketBias
from smartmoney.models.structure_event import StructureEvent
from smartmoney.models.structure_level import StructureLevel
from smartmoney.models.swing import Swing


def make_context(
    *,
    bias=MarketBias.BULLISH,
    level_price=100.0,
    candle_open=100.0,
    candle_close=102.0,
    candle_high=103.0,
    candle_low=99.0,
    swing_index=0,
):
    df = pd.DataFrame(
        [
            {
                "open": candle_open,
                "high": candle_high,
                "low": candle_low,
                "close": candle_close,
            }
        ]
    )

    context = MarketContext(
        symbol="TEST",
        timeframe=3,
        df=df,
    )

    context.market_structure.bias = bias

    if bias == MarketBias.BULLISH:
        context.market_structure.structural_high = StructureLevel(
            price=level_price,
            swing_index=swing_index,
        )
        context.swings.append(
            Swing(
                index=swing_index,
                time=pd.Timestamp("2026-01-01"),
                price=level_price,
                is_high=True,
            )
        )

    elif bias == MarketBias.BEARISH:
        context.market_structure.structural_low = StructureLevel(
            price=level_price,
            swing_index=swing_index,
        )
        context.swings.append(
            Swing(
                index=swing_index,
                time=pd.Timestamp("2026-01-01"),
                price=level_price,
                is_high=False,
            )
        )

    return context


def test_bullish_bos_increments_count_once():
    context = make_context(
        bias=MarketBias.BULLISH,
        level_price=100.0,
        candle_open=100.0,
        candle_close=102.0,
    )

    engine = MarketStructureEngine()
    engine.update(context, [])

    assert context.market_structure.bos_count == 1


def test_bullish_bos_is_not_counted_twice():
    context = make_context(
        bias=MarketBias.BULLISH,
        level_price=100.0,
        candle_open=100.0,
        candle_close=102.0,
    )

    engine = MarketStructureEngine()

    engine.update(context, [])
    engine.update(context, [])

    assert context.market_structure.bos_count == 1


def test_bullish_bos_requires_close_above_level():
    context = make_context(
        bias=MarketBias.BULLISH,
        level_price=100.0,
        candle_open=99.0,
        candle_close=100.0,
        candle_high=101.0,
    )

    engine = MarketStructureEngine()
    engine.update(context, [])

    assert context.market_structure.bos_count == 0


def test_bearish_bos_increments_count_once():
    context = make_context(
        bias=MarketBias.BEARISH,
        level_price=100.0,
        candle_open=100.0,
        candle_close=98.0,
        candle_high=101.0,
        candle_low=97.0,
    )

    engine = MarketStructureEngine()
    engine.update(context, [])

    # Bearish BOS should increment the count when price closes below the structural low.
    assert context.market_structure.bos_count == 1

def test_bearish_bos_is_not_counted_twice():
    context = make_context(
        bias=MarketBias.BEARISH,
        level_price=100.0,
        candle_open=100.0,
        candle_close=98.0,
        candle_high=101.0,
        candle_low=97.0,
    )

    engine = MarketStructureEngine()

    engine.update(context, [])
    engine.update(context, [])
