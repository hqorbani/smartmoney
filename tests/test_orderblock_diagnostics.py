from dataclasses import dataclass

from smartmoney.backtesting.orderblock_zones import OrderBlockDepthZone
from smartmoney.backtesting.outcome import TradeOutcome
from smartmoney.backtesting.runner import BacktestTrade

import pandas as pd

from smartmoney.backtesting.orderblock_diagnostics import (
    analyze_orderblock_diagnostics,
)

def make_trade(
    zone: OrderBlockDepthZone,
    outcome_1r: TradeOutcome | None,
    outcome_2r: TradeOutcome | None,
    touch_index: int,
) -> BacktestTrade:
    from smartmoney.models.orderblock import OrderBlock

    ob = OrderBlock(
        index=touch_index - 2,
        time=pd.Timestamp("2026-01-01"),
        open=100.0,
        high=110.0,
        low=90.0,
        close=95.0,
        bullish=True,
    )

    def make_outcome(
        outcome: TradeOutcome | None,
    ):
        if outcome is None:
            return None

        from smartmoney.backtesting.outcome import TradeOutcomeResult

        return TradeOutcomeResult(
            entry_price=100.0,
            stop_loss=90.0,
            take_profit=110.0,
            risk=10.0,
            reward=10.0,
            outcome=outcome,
            exit_index=touch_index + 1
            if outcome is not TradeOutcome.UNRESOLVED
            else None,
            exit_price=110.0
            if outcome is TradeOutcome.WIN
            else 90.0
            if outcome is TradeOutcome.LOSS
            else None,
            mfe=0.0,
            mae=0.0,
        )

    return BacktestTrade(
        orderblock=ob,
        touch_index=touch_index,
        touch_zone=zone,
        penetration=0.5,
        max_ob_penetration=0.5,
        entry_price=100.0,
        outcome_1r=make_outcome(outcome_1r),
        outcome_2r=make_outcome(outcome_2r),
    )


def test_diagnostics_separates_zero_risk_from_unresolved():
    trades = [
        make_trade(
            OrderBlockDepthZone.FINAL,
            None,
            None,
            touch_index=90,
        ),
        make_trade(
            OrderBlockDepthZone.FINAL,
            TradeOutcome.UNRESOLVED,
            TradeOutcome.UNRESOLVED,
            touch_index=95,
        ),
        make_trade(
            OrderBlockDepthZone.FINAL,
            TradeOutcome.WIN,
            TradeOutcome.LOSS,
            touch_index=50,
        ),
    ]

    diagnostics = analyze_orderblock_diagnostics(
        trades,
        candle_count=100,
    )

    final = diagnostics[OrderBlockDepthZone.FINAL]

    assert final.touches == 3
    assert final.zero_risk_touches == 1

    assert final.resolved_1r == 1
    assert final.unresolved_1r == 1

    assert final.resolved_2r == 1
    assert final.unresolved_2r == 1


def test_diagnostics_counts_unresolved_by_distance_from_dataset_end():
    trades = [
        make_trade(
            OrderBlockDepthZone.FINAL,
            TradeOutcome.UNRESOLVED,
            TradeOutcome.UNRESOLVED,
            touch_index=99,
        ),
        make_trade(
            OrderBlockDepthZone.FINAL,
            TradeOutcome.UNRESOLVED,
            TradeOutcome.UNRESOLVED,
            touch_index=95,
        ),
        make_trade(
            OrderBlockDepthZone.FINAL,
            TradeOutcome.UNRESOLVED,
            TradeOutcome.UNRESOLVED,
            touch_index=80,
        ),
        make_trade(
            OrderBlockDepthZone.FINAL,
            TradeOutcome.UNRESOLVED,
            TradeOutcome.UNRESOLVED,
            touch_index=50,
        ),
    ]

    diagnostics = analyze_orderblock_diagnostics(
        trades,
        candle_count=100,
    )

    final = diagnostics[OrderBlockDepthZone.FINAL]

    assert final.unresolved_1r == 4
    assert final.unresolved_2r == 4

    assert final.unresolved_1r_last_10 == 2
    assert final.unresolved_1r_last_20 == 3
    assert final.unresolved_1r_last_50 == 4
    assert final.unresolved_1r_last_100 == 4

    assert final.unresolved_2r_last_10 == 2
    assert final.unresolved_2r_last_20 == 3
    assert final.unresolved_2r_last_50 == 4
    assert final.unresolved_2r_last_100 == 4


def test_diagnostics_returns_zeroes_for_zone_without_touches():
    trades = [
        make_trade(
            OrderBlockDepthZone.FIRST,
            TradeOutcome.WIN,
            TradeOutcome.WIN,
            touch_index=10,
        ),
    ]

    diagnostics = analyze_orderblock_diagnostics(
        trades,
        candle_count=100,
    )

    middle = diagnostics[OrderBlockDepthZone.MIDDLE]

    assert middle.touches == 0
    assert middle.zero_risk_touches == 0
    assert middle.resolved_1r == 0
    assert middle.unresolved_1r == 0
    assert middle.resolved_2r == 0
    assert middle.unresolved_2r == 0

@dataclass(frozen=True, slots=True)
class OrderBlockZoneDiagnostics:
    zone: OrderBlockDepthZone
    touches: int
    zero_risk_touches: int

    resolved_1r: int
    unresolved_1r: int

    resolved_2r: int
    unresolved_2r: int

    unresolved_1r_last_10: int
    unresolved_1r_last_20: int
    unresolved_1r_last_50: int
    unresolved_1r_last_100: int

    unresolved_2r_last_10: int
    unresolved_2r_last_20: int
    unresolved_2r_last_50: int
    unresolved_2r_last_100: int


def analyze_orderblock_diagnostics(
    trades: list[BacktestTrade],
    candle_count: int,
) -> dict[OrderBlockDepthZone, OrderBlockZoneDiagnostics]:
    """
    Diagnose why first-touch observations do not produce resolved outcomes.

    zero_risk_touches are trades whose outcome is None because the first-touch
    entry leaves no positive risk.

    unresolved outcomes are trades that had a valid positive-risk entry but
    neither TP nor SL was reached before the historical dataset ended.

    The *_last_N fields count unresolved outcomes whose first touch occurred
    within the final N candles of the historical dataset.
    """
    if candle_count < 0:
        raise ValueError("candle_count must be non-negative")

    results: dict[OrderBlockDepthZone, OrderBlockZoneDiagnostics] = {}

    for zone in OrderBlockDepthZone:
        zone_trades = [
            trade for trade in trades
            if trade.touch_zone is zone
        ]

        zero_risk_touches = sum(
            trade.outcome_1r is None
            for trade in zone_trades
        )

        unresolved_1r_trades = [
            trade
            for trade in zone_trades
            if (
                trade.outcome_1r is not None
                and trade.outcome_1r.outcome is TradeOutcome.UNRESOLVED
            )
        ]

        unresolved_2r_trades = [
            trade
            for trade in zone_trades
            if (
                trade.outcome_2r is not None
                and trade.outcome_2r.outcome is TradeOutcome.UNRESOLVED
            )
        ]

        resolved_1r = sum(
            trade.outcome_1r is not None
            and trade.outcome_1r.outcome is not TradeOutcome.UNRESOLVED
            for trade in zone_trades
        )

        resolved_2r = sum(
            trade.outcome_2r is not None
            and trade.outcome_2r.outcome is not TradeOutcome.UNRESOLVED
            for trade in zone_trades
        )

        def bars_remaining(trade: BacktestTrade) -> int:
            return candle_count - 1 - trade.touch_index

        def within_last(
            trade: BacktestTrade,
            bars: int,
        ) -> bool:
            remaining = bars_remaining(trade)
            return 0 <= remaining < bars

        results[zone] = OrderBlockZoneDiagnostics(
            zone=zone,
            touches=len(zone_trades),
            zero_risk_touches=zero_risk_touches,
            resolved_1r=resolved_1r,
            unresolved_1r=len(unresolved_1r_trades),
            resolved_2r=resolved_2r,
            unresolved_2r=len(unresolved_2r_trades),
            unresolved_1r_last_10=sum(
                within_last(trade, 10)
                for trade in unresolved_1r_trades
            ),
            unresolved_1r_last_20=sum(
                within_last(trade, 20)
                for trade in unresolved_1r_trades
            ),
            unresolved_1r_last_50=sum(
                within_last(trade, 50)
                for trade in unresolved_1r_trades
            ),
            unresolved_1r_last_100=sum(
                within_last(trade, 100)
                for trade in unresolved_1r_trades
            ),
            unresolved_2r_last_10=sum(
                within_last(trade, 10)
                for trade in unresolved_2r_trades
            ),
            unresolved_2r_last_20=sum(
                within_last(trade, 20)
                for trade in unresolved_2r_trades
            ),
            unresolved_2r_last_50=sum(
                within_last(trade, 50)
                for trade in unresolved_2r_trades
            ),
            unresolved_2r_last_100=sum(
                within_last(trade, 100)
                for trade in unresolved_2r_trades
            ),
        )

    return results