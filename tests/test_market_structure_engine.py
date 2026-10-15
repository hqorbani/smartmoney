import pandas as pd

from smartmoney.core.context import MarketContext
from smartmoney.core.market_structure_engine import MarketStructureEngine
from smartmoney.models.market_structure import MarketBias
from smartmoney.models.structure_event import StructureEvent, StructureEventType
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
                "time": pd.Timestamp("2026-01-03"),
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


def test_bullish_bos_emits_event():
    context = make_context(
        bias=MarketBias.BULLISH,
        level_price=100.0,
        candle_open=100.0,
        candle_close=102.0,
    )

    engine = MarketStructureEngine()
    events = []

    engine.update(context, events)

    assert any(
        event.type.name == "BULLISH_BOS"
        for event in events
    )


def test_bearish_bos_emits_event():
    context = make_context(
        bias=MarketBias.BEARISH,
        level_price=100.0,
        candle_open=100.0,
        candle_close=98.0,
        candle_high=101.0,
        candle_low=97.0,
    )

    engine = MarketStructureEngine()
    events = []

    engine.update(context, events)

    assert any(
        event.type.name == "BEARISH_BOS"
        for event in events
    )

def test_bullish_bos_event_is_not_emitted_twice():
    context = make_context(
        bias=MarketBias.BULLISH,
        level_price=100.0,
        candle_open=100.0,
        candle_close=102.0,
    )

    engine = MarketStructureEngine()
    events = []

    engine.update(context, events)
    engine.update(context, events)

    bullish_bos_events = [
        event
        for event in events
        if event.type.name == "BULLISH_BOS"
    ]

    assert len(bullish_bos_events) == 1


def test_bearish_bos_event_is_not_emitted_twice():
    context = make_context(
        bias=MarketBias.BEARISH,
        level_price=100.0,
        candle_open=100.0,
        candle_close=98.0,
        candle_high=101.0,
        candle_low=97.0,
    )

    engine = MarketStructureEngine()
    events = []

    engine.update(context, events)
    engine.update(context, events)

    bearish_bos_events = [
        event
        for event in events
        if event.type.name == "BEARISH_BOS"
    ]

    assert len(bearish_bos_events) == 1

def test_bearish_choch_breaks_protected_low_once():
    context = make_context(
        bias=MarketBias.BULLISH,
        candle_open=102.0,
        candle_close=98.0,
        candle_high=103.0,
        candle_low=97.0,
    )

    protected_index = 1
    context.market_structure.protected_low = StructureLevel(
        price=100.0,
        swing_index=protected_index,
    )
    context.swings.append(
        Swing(
            index=protected_index,
            time=pd.Timestamp("2026-01-02"),
            price=100.0,
            is_high=False,
        )
    )

    engine = MarketStructureEngine()
    events = []

    engine.update(context, events)
    engine.update(context, events)

    assert context.market_structure.bias == MarketBias.BEARISH
    assert context.market_structure.choch_count == 1
    assert sum(
        event.type == StructureEventType.BEARISH_CHOCH
        for event in events
    ) == 1


def test_bullish_choch_breaks_protected_high_once():
    context = make_context(
        bias=MarketBias.BEARISH,
        candle_open=98.0,
        candle_close=102.0,
        candle_high=103.0,
        candle_low=97.0,
    )

    protected_index = 1
    context.market_structure.protected_high = StructureLevel(
        price=100.0,
        swing_index=protected_index,
    )
    context.swings.append(
        Swing(
            index=protected_index,
            time=pd.Timestamp("2026-01-02"),
            price=100.0,
            is_high=True,
        )
    )

    engine = MarketStructureEngine()
    events = []

    engine.update(context, events)
    engine.update(context, events)

    assert context.market_structure.bias == MarketBias.BULLISH
    assert context.market_structure.choch_count == 1
    assert sum(
        event.type == StructureEventType.BULLISH_CHOCH
        for event in events
    ) == 1

def test_bearish_choch_is_not_emitted_above_protected_low():
    context = make_context(
        bias=MarketBias.BULLISH,
        candle_open=102.0,
        candle_close=101.0,
        candle_high=103.0,
        candle_low=100.5,
    )

    protected_index = 1
    context.market_structure.protected_low = StructureLevel(
        price=100.0,
        swing_index=protected_index,
    )
    context.swings.append(
        Swing(
            index=protected_index,
            time=pd.Timestamp("2026-01-02"),
            price=100.0,
            is_high=False,
        )
    )

    engine = MarketStructureEngine()
    events = []

    engine.update(context, events)

    assert context.market_structure.bias == MarketBias.BULLISH
    assert context.market_structure.choch_count == 0
    assert not any(
        event.type == StructureEventType.BEARISH_CHOCH
        for event in events
    )


def test_bullish_choch_is_not_emitted_below_protected_high():
    context = make_context(
        bias=MarketBias.BEARISH,
        candle_open=98.0,
        candle_close=99.0,
        candle_high=99.5,
        candle_low=97.0,
    )

    protected_index = 1
    context.market_structure.protected_high = StructureLevel(
        price=100.0,
        swing_index=protected_index,
    )
    context.swings.append(
        Swing(
            index=protected_index,
            time=pd.Timestamp("2026-01-02"),
            price=100.0,
            is_high=True,
        )
    )

    engine = MarketStructureEngine()
    events = []

    engine.update(context, events)

    assert context.market_structure.bias == MarketBias.BEARISH
    assert context.market_structure.choch_count == 0
    assert not any(
        event.type == StructureEventType.BULLISH_CHOCH
        for event in events
    )

def test_bearish_choch_does_not_emit_bearish_bos_on_same_update():
    context = make_context(
        bias=MarketBias.BULLISH,
        candle_open=102.0,
        candle_close=98.0,
        candle_high=103.0,
        candle_low=97.0,
    )

    protected_index = 1
    context.market_structure.protected_low = StructureLevel(
        price=100.0,
        swing_index=protected_index,
    )
    context.swings.append(
        Swing(
            index=protected_index,
            time=pd.Timestamp("2026-01-02"),
            price=100.0,
            is_high=False,
        )
    )

    engine = MarketStructureEngine()
    events = []

    engine.update(context, events)

    assert context.market_structure.bias == MarketBias.BEARISH
    assert any(
        event.type == StructureEventType.BEARISH_CHOCH
        for event in events
    )
    assert not any(
        event.type == StructureEventType.BEARISH_BOS
        for event in events
    )


def test_bearish_choch_does_not_use_stale_structural_low_for_bos():
    context = make_context(
        bias=MarketBias.BULLISH,
        candle_open=102.0,
        candle_close=98.0,
        candle_high=103.0,
        candle_low=97.0,
    )

    context.market_structure.protected_low = StructureLevel(
        price=100.0,
        swing_index=1,
    )
    context.market_structure.structural_low = StructureLevel(
        price=99.0,
        swing_index=0,
    )

    context.swings.extend([
        Swing(
            index=0,
            time=pd.Timestamp("2026-01-01"),
            price=99.0,
            is_high=False,
        ),
        Swing(
            index=1,
            time=pd.Timestamp("2026-01-02"),
            price=100.0,
            is_high=False,
        ),
    ])

    engine = MarketStructureEngine()
    events = []

    engine.update(context, events)

    assert context.market_structure.bias == MarketBias.BEARISH
    assert any(
        event.type == StructureEventType.BEARISH_CHOCH
        for event in events
    )

    context.df.loc[context.df.index[-1], "open"] = 98.0
    context.df.loc[context.df.index[-1], "close"] = 97.0

    events = []
    engine.update(context, events)

    assert not any(
        event.type == StructureEventType.BEARISH_BOS
        for event in events
    )

def test_find_swing_after_choch_selects_latest_matching_swing():
    context = make_context(bias=MarketBias.BEARISH)
    context.market_structure.choch_time = pd.Timestamp("2026-01-03")

    context.swings.extend([
        Swing(
            index=1,
            time=pd.Timestamp("2026-01-02"),
            price=95.0,
            is_high=False,
        ),
        Swing(
            index=2,
            time=pd.Timestamp("2026-01-04"),
            price=92.0,
            is_high=False,
        ),
        Swing(
            index=3,
            time=pd.Timestamp("2026-01-05"),
            price=90.0,
            is_high=False,
        ),
        Swing(
            index=4,
            time=pd.Timestamp("2026-01-06"),
            price=105.0,
            is_high=True,
        ),
    ])

    engine = MarketStructureEngine()

    swing = engine._find_swing_after_choch(
        context,
        is_high=False,
    )

    assert swing is not None
    assert swing.index == 3
    assert swing.price == 90.0


def test_choch_rebuilds_structure_and_allows_bos():
    context = make_context(
        bias=MarketBias.BULLISH,
        candle_open=102.0,
        candle_close=98.0,
        candle_high=103.0,
        candle_low=97.0,
    )

    structure = context.market_structure
    structure.protected_low = StructureLevel(
        price=100.0,
        swing_index=1,
    )
    structure.structural_low = StructureLevel(
        price=99.0,
        swing_index=0,
    )

    context.swings.append(
        Swing(
            index=1,
            time=pd.Timestamp("2026-01-02"),
            price=100.0,
            is_high=False,
        )
    )

    engine = MarketStructureEngine()
    events = []

    # مرحله اول: CHOCH باید سطح ساختاری قدیمی را پاک کند.
    engine.update(context, events)

    assert structure.bias == MarketBias.BEARISH
    assert structure.structural_low.price is None
    assert any(
        event.type == StructureEventType.BEARISH_CHOCH
        for event in events
    )
    assert not any(
        event.type == StructureEventType.BEARISH_BOS
        for event in events
    )

    # مرحله دوم: یک swing low جدید بعد از CHOCH تشکیل می‌شود.
    context.swings.append(
        Swing(
            index=2,
            time=pd.Timestamp("2026-01-04"),
            price=95.0,
            is_high=False,
        )
    )

    # مرحله سوم: قیمت زیر swing low جدید بسته می‌شود.
    context.df.loc[context.df.index[-1], "time"] = pd.Timestamp(
        "2026-01-05"
    )
    context.df.loc[context.df.index[-1], "open"] = 94.0
    context.df.loc[context.df.index[-1], "high"] = 94.5
    context.df.loc[context.df.index[-1], "low"] = 92.0
    context.df.loc[context.df.index[-1], "close"] = 93.0

    events = []
    engine.update(context, events)

    assert structure.structural_low.price == 95.0
    assert structure.structural_low.swing_index == 2
    assert structure.bos_count == 1
    assert any(
        event.type == StructureEventType.BEARISH_BOS
        for event in events
    )

def test_bullish_bos_can_be_detected_on_two_distinct_levels():
    context = make_context(
        bias=MarketBias.BULLISH,
        candle_open=105.0,
        candle_close=111.0,
        candle_high=112.0,
        candle_low=104.0,
    )

    structure = context.market_structure
    structure.structural_high = StructureLevel(
        price=100.0,
        swing_index=1,
    )

    context.swings.extend([
        Swing(
            index=1,
            time=pd.Timestamp("2026-01-01"),
            price=100.0,
            is_high=True,
        ),
        Swing(
            index=2,
            time=pd.Timestamp("2026-01-02"),
            price=110.0,
            is_high=True,
        ),
    ])

    engine = MarketStructureEngine()
    events = []

    engine.update(context, events)

    assert structure.bos_count == 1
    assert any(
        event.type == StructureEventType.BULLISH_BOS
        for event in events
    )

    # سطح بعدی شکسته می‌شود.
    structure.structural_high = StructureLevel(
        price=110.0,
        swing_index=2,
    )

    context.df.loc[context.df.index[-1], "open"] = 115.0
    context.df.loc[context.df.index[-1], "close"] = 121.0
    context.df.loc[context.df.index[-1], "high"] = 122.0
    context.df.loc[context.df.index[-1], "low"] = 114.0

    events = []
    engine.update(context, events)

    assert structure.bos_count == 2
    assert any(
        event.type == StructureEventType.BULLISH_BOS
        for event in events
    )


def test_bearish_bos_can_be_detected_on_two_distinct_levels():
    context = make_context(
        bias=MarketBias.BEARISH,
        candle_open=95.0,
        candle_close=89.0,
        candle_high=96.0,
        candle_low=88.0,
    )

    structure = context.market_structure
    structure.structural_low = StructureLevel(
        price=100.0,
        swing_index=1,
    )

    context.swings.extend([
        Swing(
            index=1,
            time=pd.Timestamp("2026-01-01"),
            price=100.0,
            is_high=False,
        ),
        Swing(
            index=2,
            time=pd.Timestamp("2026-01-02"),
            price=90.0,
            is_high=False,
        ),
    ])

    engine = MarketStructureEngine()
    events = []

    engine.update(context, events)

    assert structure.bos_count == 1
    assert any(
        event.type == StructureEventType.BEARISH_BOS
        for event in events
    )

    # سطح بعدی شکسته می‌شود.
    structure.structural_low = StructureLevel(
        price=90.0,
        swing_index=2,
    )

    context.df.loc[context.df.index[-1], "open"] = 85.0
    context.df.loc[context.df.index[-1], "close"] = 79.0
    context.df.loc[context.df.index[-1], "high"] = 86.0
    context.df.loc[context.df.index[-1], "low"] = 78.0

    events = []
    engine.update(context, events)

    assert structure.bos_count == 2
    assert any(
        event.type == StructureEventType.BEARISH_BOS
        for event in events
    )

def test_bullish_bos_updates_protected_low_to_latest_swing():
    context = make_context(
        bias=MarketBias.BULLISH,
        level_price=100.0,
        candle_open=100.0,
        candle_close=102.0,
    )

    context.swings.extend([
        Swing(
            index=1,
            time=pd.Timestamp("2026-01-02"),
            price=97.0,
            is_high=False,
        ),
        Swing(
            index=2,
            time=pd.Timestamp("2026-01-02 12:00"),
            price=98.0,
            is_high=False,
        ),
    ])

    engine = MarketStructureEngine()
    engine.update(context, [])

    structure = context.market_structure

    assert structure.bos_count == 1
    assert structure.protected_low.price == 98.0
    assert structure.protected_low.swing_index == 2


def test_bearish_bos_updates_protected_high_to_latest_swing():
    context = make_context(
        bias=MarketBias.BEARISH,
        level_price=100.0,
        candle_open=100.0,
        candle_close=98.0,
        candle_high=101.0,
        candle_low=97.0,
    )

    context.swings.extend([
        Swing(
            index=1,
            time=pd.Timestamp("2026-01-02"),
            price=103.0,
            is_high=True,
        ),
        Swing(
            index=2,
            time=pd.Timestamp("2026-01-02 12:00"),
            price=102.0,
            is_high=True,
        ),
    ])

    engine = MarketStructureEngine()
    engine.update(context, [])

    structure = context.market_structure

    assert structure.bos_count == 1
    assert structure.protected_high.price == 102.0
    assert structure.protected_high.swing_index == 2


def test_bearish_choch_clears_old_protected_low():
    context = make_context(
        bias=MarketBias.BULLISH,
        candle_open=102.0,
        candle_close=98.0,
    )

    structure = context.market_structure
    structure.protected_low = StructureLevel(
        price=100.0,
        swing_index=1,
    )
    context.swings.append(
        Swing(
            index=1,
            time=pd.Timestamp("2026-01-02"),
            price=100.0,
            is_high=False,
        )
    )

    MarketStructureEngine().update(context, [])

    assert structure.bias == MarketBias.BEARISH
    assert structure.protected_low.price is None
    assert structure.protected_low.swing_index is None


def test_bullish_choch_clears_old_protected_high():
    context = make_context(
        bias=MarketBias.BEARISH,
        candle_open=98.0,
        candle_close=102.0,
    )

    structure = context.market_structure
    structure.protected_high = StructureLevel(
        price=100.0,
        swing_index=1,
    )
    context.swings.append(
        Swing(
            index=1,
            time=pd.Timestamp("2026-01-02"),
            price=100.0,
            is_high=True,
        )
    )

    MarketStructureEngine().update(context, [])

    assert structure.bias == MarketBias.BULLISH
    assert structure.protected_high.price is None
    assert structure.protected_high.swing_index is None


def test_bearish_choch_then_bos_restores_protected_high():
    context = make_context(
        bias=MarketBias.BULLISH,
        candle_open=102.0,
        candle_close=98.0,
        candle_high=103.0,
        candle_low=97.0,
    )

    structure = context.market_structure
    structure.protected_low = StructureLevel(
        price=100.0,
        swing_index=1,
    )

    context.swings.append(
        Swing(
            index=1,
            time=pd.Timestamp("2026-01-02"),
            price=100.0,
            is_high=False,
        )
    )

    engine = MarketStructureEngine()
    engine.update(context, [])

    assert structure.bias == MarketBias.BEARISH
    assert structure.protected_low.price is None

    context.swings.extend([
        Swing(
            index=2,
            time=pd.Timestamp("2026-01-04"),
            price=99.0,
            is_high=True,
        ),
        Swing(
            index=3,
            time=pd.Timestamp("2026-01-04 12:00"),
            price=95.0,
            is_high=False,
        ),
    ])

    context.df.loc[context.df.index[-1], "time"] = pd.Timestamp(
        "2026-01-05"
    )
    context.df.loc[context.df.index[-1], "open"] = 94.0
    context.df.loc[context.df.index[-1], "high"] = 94.5
    context.df.loc[context.df.index[-1], "low"] = 92.0
    context.df.loc[context.df.index[-1], "close"] = 93.0

    events = []
    engine.update(context, events)

    assert structure.bos_count == 1
    assert structure.protected_high.price == 99.0
    assert structure.protected_high.swing_index == 2


def test_bullish_choch_then_bos_restores_protected_low():
    context = make_context(
        bias=MarketBias.BEARISH,
        candle_open=98.0,
        candle_close=102.0,
        candle_high=103.0,
        candle_low=97.0,
    )

    structure = context.market_structure
    structure.protected_high = StructureLevel(
        price=100.0,
        swing_index=1,
    )

    context.swings.append(
        Swing(
            index=1,
            time=pd.Timestamp("2026-01-02"),
            price=100.0,
            is_high=True,
        )
    )

    engine = MarketStructureEngine()
    engine.update(context, [])

    assert structure.bias == MarketBias.BULLISH
    assert structure.protected_high.price is None

    context.swings.extend([
        Swing(
            index=2,
            time=pd.Timestamp("2026-01-04"),
            price=101.0,
            is_high=False,
        ),
        Swing(
            index=3,
            time=pd.Timestamp("2026-01-04 12:00"),
            price=105.0,
            is_high=True,
        ),
    ])

    context.df.loc[context.df.index[-1], "time"] = pd.Timestamp(
        "2026-01-05"
    )
    context.df.loc[context.df.index[-1], "open"] = 106.0
    context.df.loc[context.df.index[-1], "high"] = 108.0
    context.df.loc[context.df.index[-1], "low"] = 105.5
    context.df.loc[context.df.index[-1], "close"] = 107.0

    events = []
    engine.update(context, events)

    assert structure.bos_count == 1
    assert structure.protected_low.price == 101.0
    assert structure.protected_low.swing_index == 2
