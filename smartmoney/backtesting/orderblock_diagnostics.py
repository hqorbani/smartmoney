from dataclasses import dataclass

from smartmoney.backtesting.orderblock_zones import OrderBlockDepthZone
from smartmoney.backtesting.outcome import TradeOutcome
from smartmoney.backtesting.runner import BacktestTrade


@dataclass(frozen=True, slots=True)
class OrderBlockZoneDiagnostics:
    zone: OrderBlockDepthZone
    touches: int
    zero_risk_touches : int

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
    Diagnose unresolved and non-tradable first-touch observations.

    `candle_count` is the total number of historical candles used by the
    backtest.

    A trade is considered zero-risk when either outcome is missing because
    the entry price does not leave positive risk.

    An unresolved outcome is classified by the number of candles remaining
    after the first-touch candle when the historical window ended.
    """
    if candle_count < 0:
        raise ValueError("candle_count must be non-negative")

    results: dict[
        OrderBlockDepthZone,
        OrderBlockZoneDiagnostics,
    ] = {}

    for zone in OrderBlockDepthZone:
        zone_trades = [
            trade
            for trade in trades
            if trade.touch_zone is zone
        ]

        zero_risk_touches  = sum(
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
            and trade.outcome_1r.outcome in {
                TradeOutcome.WIN,
                TradeOutcome.LOSS,
            }
            for trade in zone_trades
        )

        resolved_2r = sum(
            trade.outcome_2r is not None
            and trade.outcome_2r.outcome in {
                TradeOutcome.WIN,
                TradeOutcome.LOSS,
            }
            for trade in zone_trades
        )

        def bars_remaining(trade: BacktestTrade) -> int:
            return candle_count - 1 - trade.touch_index

        def count_within(
            unresolved_trades: list[BacktestTrade],
            limit: int,
        ) -> int:
            return sum(
                0 <= bars_remaining(trade) < limit
                for trade in unresolved_trades
            )

        results[zone] = OrderBlockZoneDiagnostics(
            zone=zone,
            touches=len(zone_trades),
            zero_risk_touches =zero_risk_touches ,
            resolved_1r=resolved_1r,
            unresolved_1r=len(unresolved_1r_trades),
            resolved_2r=resolved_2r,
            unresolved_2r=len(unresolved_2r_trades),
            unresolved_1r_last_10=count_within(
                unresolved_1r_trades,
                10,
            ),
            unresolved_1r_last_20=count_within(
                unresolved_1r_trades,
                20,
            ),
            unresolved_1r_last_50=count_within(
                unresolved_1r_trades,
                50,
            ),
            unresolved_1r_last_100=count_within(
                unresolved_1r_trades,
                100,
            ),
            unresolved_2r_last_10=count_within(
                unresolved_2r_trades,
                10,
            ),
            unresolved_2r_last_20=count_within(
                unresolved_2r_trades,
                20,
            ),
            unresolved_2r_last_50=count_within(
                unresolved_2r_trades,
                50,
            ),
            unresolved_2r_last_100=count_within(
                unresolved_2r_trades,
                100,
            ),
        )

    return results