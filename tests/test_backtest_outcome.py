import pandas as pd
import pytest

from smartmoney.backtesting.outcome import (
    TradeOutcome,
    calculate_entry_price,
    calculate_trade_levels,
    simulate_outcome,
)
from smartmoney.models.orderblock import OrderBlock


def make_orderblock(bullish: bool) -> OrderBlock:
    return OrderBlock(
        index=0,
        time=pd.Timestamp("2026-01-01"),
        open=95.0,
        high=100.0,
        low=90.0,
        close=95.0,
        bullish=bullish,
    )


def test_bullish_entry_uses_actual_touch_price():
    ob = make_orderblock(True)

    entry = calculate_entry_price(
        ob,
        candle_low=98.0,
        candle_high=101.0,
    )

    assert entry == pytest.approx(98.0)


def test_bearish_entry_uses_actual_touch_price():
    ob = make_orderblock(False)

    entry = calculate_entry_price(
        ob,
        candle_low=89.0,
        candle_high=92.0,
    )

    assert entry == pytest.approx(92.0)


def test_bullish_trade_levels_at_1r():
    ob = make_orderblock(True)

    stop_loss, take_profit, risk = calculate_trade_levels(
        ob,
        entry_price=98.0,
        rr=1.0,
    )

    assert stop_loss == pytest.approx(90.0)
    assert risk == pytest.approx(8.0)
    assert take_profit == pytest.approx(106.0)


def test_bearish_trade_levels_at_2r():
    ob = make_orderblock(False)

    stop_loss, take_profit, risk = calculate_trade_levels(
        ob,
        entry_price=92.0,
        rr=2.0,
    )

    assert stop_loss == pytest.approx(100.0)
    assert risk == pytest.approx(8.0)
    assert take_profit == pytest.approx(76.0)


def test_bullish_trade_wins_at_1r():
    ob = make_orderblock(True)

    df = pd.DataFrame(
        [
            {"low": 98.0, "high": 101.0},
            {"low": 97.0, "high": 106.0},
        ]
    )

    result = simulate_outcome(
        df=df,
        ob=ob,
        touch_index=0,
        entry_price=98.0,
        rr=1.0,
    )

    assert result.outcome is TradeOutcome.WIN
    assert result.exit_index == 1
    assert result.exit_price == pytest.approx(106.0)
    assert result.mfe == pytest.approx(8.0)
    assert result.mae == pytest.approx(1.0)


def test_bullish_trade_loses_at_1r():
    ob = make_orderblock(True)

    df = pd.DataFrame(
        [
            {"low": 98.0, "high": 101.0},
            {"low": 89.0, "high": 99.0},
        ]
    )

    result = simulate_outcome(
        df=df,
        ob=ob,
        touch_index=0,
        entry_price=98.0,
        rr=1.0,
    )

    assert result.outcome is TradeOutcome.LOSS
    assert result.exit_index == 1
    assert result.exit_price == pytest.approx(90.0)


def test_bearish_trade_wins_at_2r():
    ob = make_orderblock(False)

    df = pd.DataFrame(
        [
            {"low": 89.0, "high": 92.0},
            {"low": 76.0, "high": 93.0},
        ]
    )

    result = simulate_outcome(
        df=df,
        ob=ob,
        touch_index=0,
        entry_price=92.0,
        rr=2.0,
    )

    assert result.outcome is TradeOutcome.WIN
    assert result.exit_index == 1
    assert result.exit_price == pytest.approx(76.0)


def test_unresolved_trade_is_not_counted_as_win_or_loss():
    ob = make_orderblock(True)

    df = pd.DataFrame(
        [
            {"low": 98.0, "high": 101.0},
            {"low": 95.0, "high": 103.0},
        ]
    )

    result = simulate_outcome(
        df=df,
        ob=ob,
        touch_index=0,
        entry_price=98.0,
        rr=1.0,
    )

    assert result.outcome is TradeOutcome.UNRESOLVED
    assert result.exit_index is None
    assert result.exit_price is None


def test_same_candle_stop_and_target_is_conservative_loss():
    ob = make_orderblock(True)

    df = pd.DataFrame(
        [
            {"low": 98.0, "high": 101.0},
            {"low": 89.0, "high": 106.0},
        ]
    )

    result = simulate_outcome(
        df=df,
        ob=ob,
        touch_index=0,
        entry_price=98.0,
        rr=1.0,
    )

    assert result.outcome is TradeOutcome.LOSS
    assert result.exit_price == pytest.approx(90.0)


def test_touch_candle_is_not_used_for_outcome():
    ob = make_orderblock(True)

    df = pd.DataFrame(
        [
            {"low": 90.0, "high": 106.0},
        ]
    )

    result = simulate_outcome(
        df=df,
        ob=ob,
        touch_index=0,
        entry_price=98.0,
        rr=1.0,
    )

    assert result.outcome is TradeOutcome.UNRESOLVED
    assert result.mfe == pytest.approx(0.0)
    assert result.mae == pytest.approx(0.0)