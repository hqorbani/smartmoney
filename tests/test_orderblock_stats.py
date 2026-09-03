import pandas as pd

from smartmoney.backtesting.orderblock_stats import analyze_orderblock_zones
from smartmoney.backtesting.orderblock_zones import OrderBlockDepthZone
from smartmoney.backtesting.outcome import TradeOutcome, TradeOutcomeResult
from smartmoney.backtesting.runner import BacktestTrade
from smartmoney.models.orderblock import OrderBlock


def make_trade(
    zone: OrderBlockDepthZone,
    outcome_1r: TradeOutcome,
    outcome_2r: TradeOutcome,
    penetration: float = 0.5,
    mfe_1r: float = 10.0,
    mae_1r: float = 2.0,
    mfe_2r: float = 12.0,
    mae_2r: float = 3.0,
) -> BacktestTrade:
    orderblock = OrderBlock(
        index=0,
        time=pd.Timestamp("2026-01-01"),
        open=100.0,
        high=100.0,
        low=90.0,
        close=95.0,
        bullish=True,
    )

    result_1r = TradeOutcomeResult(
        entry_price=95.0,
        stop_loss=90.0,
        take_profit=100.0,
        risk=5.0,
        reward=5.0,
        outcome=outcome_1r,
        exit_index=1 if outcome_1r is not TradeOutcome.UNRESOLVED else None,
        exit_price=100.0 if outcome_1r is TradeOutcome.WIN else None,
        mfe=mfe_1r,
        mae=mae_1r,
    )

    result_2r = TradeOutcomeResult(
        entry_price=95.0,
        stop_loss=90.0,
        take_profit=105.0,
        risk=5.0,
        reward=10.0,
        outcome=outcome_2r,
        exit_index=1 if outcome_2r is not TradeOutcome.UNRESOLVED else None,
        exit_price=105.0 if outcome_2r is TradeOutcome.WIN else None,
        mfe=mfe_2r,
        mae=mae_2r,
    )

    return BacktestTrade(
        orderblock=orderblock,
        touch_index=1,
        touch_zone=zone,
        penetration=penetration,
        entry_price=95.0,
        outcome_1r=result_1r,
        outcome_2r=result_2r,
    )


def test_empty_trades_return_zero_stats_for_all_zones():
    stats = analyze_orderblock_zones([])

    assert set(stats) == {
        OrderBlockDepthZone.FIRST,
        OrderBlockDepthZone.MIDDLE,
        OrderBlockDepthZone.FINAL,
    }

    for zone_stats in stats.values():
        assert zone_stats.touches == 0
        assert zone_stats.zone_frequency == 0.0

        assert zone_stats.wins_1r == 0
        assert zone_stats.losses_1r == 0
        assert zone_stats.unresolved_1r == 0

        assert zone_stats.wins_2r == 0
        assert zone_stats.losses_2r == 0
        assert zone_stats.unresolved_2r == 0

        assert zone_stats.win_rate_1r == 0.0
        assert zone_stats.win_rate_2r == 0.0


def test_zone_frequency_is_based_on_first_touch_zone():
    trades = [
        make_trade(OrderBlockDepthZone.FIRST, TradeOutcome.WIN, TradeOutcome.WIN),
        make_trade(OrderBlockDepthZone.FIRST, TradeOutcome.LOSS, TradeOutcome.WIN),
        make_trade(OrderBlockDepthZone.MIDDLE, TradeOutcome.WIN, TradeOutcome.LOSS),
        make_trade(OrderBlockDepthZone.FINAL, TradeOutcome.LOSS, TradeOutcome.LOSS),
    ]

    stats = analyze_orderblock_zones(trades)

    assert stats[OrderBlockDepthZone.FIRST].touches == 2
    assert stats[OrderBlockDepthZone.MIDDLE].touches == 1
    assert stats[OrderBlockDepthZone.FINAL].touches == 1

    assert stats[OrderBlockDepthZone.FIRST].zone_frequency == 0.5
    assert stats[OrderBlockDepthZone.MIDDLE].zone_frequency == 0.25
    assert stats[OrderBlockDepthZone.FINAL].zone_frequency == 0.25

    total_frequency = sum(
        zone_stats.zone_frequency
        for zone_stats in stats.values()
    )
    assert total_frequency == 1.0


def test_1r_win_rate_excludes_unresolved_trades():
    trades = [
        make_trade(OrderBlockDepthZone.FIRST, TradeOutcome.WIN, TradeOutcome.WIN),
        make_trade(OrderBlockDepthZone.FIRST, TradeOutcome.WIN, TradeOutcome.LOSS),
        make_trade(
            OrderBlockDepthZone.FIRST,
            TradeOutcome.LOSS,
            TradeOutcome.UNRESOLVED,
        ),
        make_trade(
            OrderBlockDepthZone.FIRST,
            TradeOutcome.UNRESOLVED,
            TradeOutcome.WIN,
        ),
    ]

    stats = analyze_orderblock_zones(trades)
    first = stats[OrderBlockDepthZone.FIRST]

    assert first.touches == 4
    assert first.wins_1r == 2
    assert first.losses_1r == 1
    assert first.unresolved_1r == 1

    assert first.resolved_1r == 3
    assert first.resolution_rate_1r == 0.75
    assert first.win_rate_1r == 2 / 3


def test_2r_win_rate_is_calculated_independently():
    trades = [
        make_trade(OrderBlockDepthZone.MIDDLE, TradeOutcome.LOSS, TradeOutcome.WIN),
        make_trade(
            OrderBlockDepthZone.MIDDLE,
            TradeOutcome.WIN,
            TradeOutcome.LOSS,
        ),
        make_trade(
            OrderBlockDepthZone.MIDDLE,
            TradeOutcome.UNRESOLVED,
            TradeOutcome.UNRESOLVED,
        ),
    ]

    stats = analyze_orderblock_zones(trades)
    middle = stats[OrderBlockDepthZone.MIDDLE]

    assert middle.wins_2r == 1
    assert middle.losses_2r == 1
    assert middle.unresolved_2r == 1

    assert middle.resolved_2r == 2
    assert middle.resolution_rate_2r == 2 / 3
    assert middle.win_rate_2r == 0.5


def test_raw_success_rate_counts_only_wins_against_all_touches():
    trades = [
        make_trade(OrderBlockDepthZone.FINAL, TradeOutcome.WIN, TradeOutcome.WIN),
        make_trade(OrderBlockDepthZone.FINAL, TradeOutcome.LOSS, TradeOutcome.LOSS),
        make_trade(
            OrderBlockDepthZone.FINAL,
            TradeOutcome.UNRESOLVED,
            TradeOutcome.UNRESOLVED,
        ),
        make_trade(
            OrderBlockDepthZone.FINAL,
            TradeOutcome.WIN,
            TradeOutcome.LOSS,
        ),
    ]

    stats = analyze_orderblock_zones(trades)
    final = stats[OrderBlockDepthZone.FINAL]

    assert final.raw_success_rate_1r == 0.5
    assert final.raw_success_rate_2r == 0.25


def test_average_penetration_and_excursions_are_calculated():
    trades = [
        make_trade(
            OrderBlockDepthZone.FIRST,
            TradeOutcome.WIN,
            TradeOutcome.WIN,
            penetration=0.2,
            mfe_1r=10.0,
            mae_1r=2.0,
            mfe_2r=20.0,
            mae_2r=4.0,
        ),
        make_trade(
            OrderBlockDepthZone.FIRST,
            TradeOutcome.LOSS,
            TradeOutcome.LOSS,
            penetration=0.8,
            mfe_1r=6.0,
            mae_1r=3.0,
            mfe_2r=12.0,
            mae_2r=6.0,
        ),
    ]

    stats = analyze_orderblock_zones(trades)
    first = stats[OrderBlockDepthZone.FIRST]

    assert first.average_penetration == 0.5
    assert first.average_mfe_1r == 8.0
    assert first.average_mae_1r == 2.5
    assert first.average_mfe_2r == 16.0
    assert first.average_mae_2r == 5.0