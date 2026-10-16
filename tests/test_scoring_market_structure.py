from types import SimpleNamespace

import pytest

from smartmoney.config import Config
from smartmoney.models.market_structure import MarketBias, MarketStructure
from smartmoney.models.signal import Signal, SignalDirection
from smartmoney.scoring.market_structure import MarketStructureAlignmentScore


@pytest.fixture
def rule():
    return MarketStructureAlignmentScore()


def make_context(bias):
    return SimpleNamespace(
        market_structure=MarketStructure(bias=bias)
    )


@pytest.mark.parametrize(
    "direction",
    [
        "BUY",
        "buy",
        SignalDirection.BUY,
    ],
)
def test_buy_signal_matches_bullish_structure(rule, direction):
    signal = Signal(direction=direction)
    context = make_context(MarketBias.BULLISH)

    assert rule.score(signal, context) == Config.MARKET_STRUCTURE_ALIGNMENT_SCORE


@pytest.mark.parametrize(
    "direction",
    [
        "SELL",
        "sell",
        SignalDirection.SELL,
    ],
)
def test_sell_signal_matches_bearish_structure(rule, direction):
    signal = Signal(direction=direction)
    context = make_context(MarketBias.BEARISH)

    assert rule.score(signal, context) == Config.MARKET_STRUCTURE_ALIGNMENT_SCORE


@pytest.mark.parametrize(
    ("direction", "bias"),
    [
        ("BUY", MarketBias.BEARISH),
        ("buy", MarketBias.BEARISH),
        (SignalDirection.BUY, MarketBias.BEARISH),
        ("SELL", MarketBias.BULLISH),
        ("sell", MarketBias.BULLISH),
        (SignalDirection.SELL, MarketBias.BULLISH),
    ],
)
def test_opposite_direction_gets_zero_score(rule, direction, bias):
    signal = Signal(direction=direction)
    context = make_context(bias)

    assert rule.score(signal, context) == 0.0


@pytest.mark.parametrize(
    "bias",
    [
        MarketBias.UNKNOWN,
        MarketBias.TRANSITION,
    ],
)
def test_unknown_or_transition_structure_gets_zero_score(rule, bias):
    signal = Signal(direction=SignalDirection.BUY)
    context = make_context(bias)

    assert rule.score(signal, context) == 0.0


def test_no_signal_direction_gets_zero_score(rule):
    signal = Signal(direction=SignalDirection.NO_SIGNAL)
    context = make_context(MarketBias.BULLISH)

    assert rule.score(signal, context) == 0.0
