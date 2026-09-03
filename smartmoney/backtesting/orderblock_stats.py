from dataclasses import dataclass

from smartmoney.backtesting.orderblock_zones import OrderBlockDepthZone
from smartmoney.backtesting.outcome import TradeOutcome
from smartmoney.backtesting.runner import BacktestTrade


@dataclass(frozen=True, slots=True)
class OrderBlockZoneStats:
    zone: OrderBlockDepthZone
    touches: int
    zone_frequency: float

    wins_1r: int
    losses_1r: int
    unresolved_1r: int

    wins_2r: int
    losses_2r: int
    unresolved_2r: int

    average_penetration: float
    average_mfe_1r: float
    average_mae_1r: float
    average_mfe_2r: float
    average_mae_2r: float

    @property
    def resolved_1r(self) -> int:
        return self.wins_1r + self.losses_1r

    @property
    def resolved_2r(self) -> int:
        return self.wins_2r + self.losses_2r

    @property
    def resolution_rate_1r(self) -> float:
        if self.touches == 0:
            return 0.0
        return self.resolved_1r / self.touches

    @property
    def resolution_rate_2r(self) -> float:
        if self.touches == 0:
            return 0.0
        return self.resolved_2r / self.touches

    @property
    def win_rate_1r(self) -> float:
        if self.resolved_1r == 0:
            return 0.0
        return self.wins_1r / self.resolved_1r

    @property
    def win_rate_2r(self) -> float:
        if self.resolved_2r == 0:
            return 0.0
        return self.wins_2r / self.resolved_2r

    @property
    def raw_success_rate_1r(self) -> float:
        if self.touches == 0:
            return 0.0
        return self.wins_1r / self.touches

    @property
    def raw_success_rate_2r(self) -> float:
        if self.touches == 0:
            return 0.0
        return self.wins_2r / self.touches


def analyze_orderblock_zones(
    trades: list[BacktestTrade],
) -> dict[OrderBlockDepthZone, OrderBlockZoneStats]:
    """
    Aggregate backtest results by the zone reached on the first touch.

    This function deliberately separates first-touch classification from
    subsequent Order Block depth reach. The `penetration` stored on
    BacktestTrade describes only the first-touch candle.

    Win rate is calculated only from resolved trades:
        wins / (wins + losses)

    Raw success rate is calculated from all first-touch trades:
        wins / touches

    Unresolved trades are therefore excluded from win rate but remain
    visible in the statistics.
    """
    total_trades = len(trades)

    results: dict[OrderBlockDepthZone, OrderBlockZoneStats] = {}

    for zone in OrderBlockDepthZone:
        zone_trades = [
            trade for trade in trades if trade.touch_zone is zone
        ]

        touches = len(zone_trades)

        wins_1r = sum(
            trade.outcome_1r.outcome is TradeOutcome.WIN
            for trade in zone_trades
        )
        losses_1r = sum(
            trade.outcome_1r.outcome is TradeOutcome.LOSS
            for trade in zone_trades
        )
        unresolved_1r = sum(
            trade.outcome_1r.outcome is TradeOutcome.UNRESOLVED
            for trade in zone_trades
        )

        wins_2r = sum(
            trade.outcome_2r.outcome is TradeOutcome.WIN
            for trade in zone_trades
        )
        losses_2r = sum(
            trade.outcome_2r.outcome is TradeOutcome.LOSS
            for trade in zone_trades
        )
        unresolved_2r = sum(
            trade.outcome_2r.outcome is TradeOutcome.UNRESOLVED
            for trade in zone_trades
        )

        if touches:
            average_penetration = sum(
                trade.penetration for trade in zone_trades
            ) / touches

            average_mfe_1r = sum(
                trade.outcome_1r.mfe for trade in zone_trades
            ) / touches

            average_mae_1r = sum(
                trade.outcome_1r.mae for trade in zone_trades
            ) / touches

            average_mfe_2r = sum(
                trade.outcome_2r.mfe for trade in zone_trades
            ) / touches

            average_mae_2r = sum(
                trade.outcome_2r.mae for trade in zone_trades
            ) / touches
        else:
            average_penetration = 0.0
            average_mfe_1r = 0.0
            average_mae_1r = 0.0
            average_mfe_2r = 0.0
            average_mae_2r = 0.0

        zone_frequency = (
            touches / total_trades
            if total_trades
            else 0.0
        )

        results[zone] = OrderBlockZoneStats(
            zone=zone,
            touches=touches,
            zone_frequency=zone_frequency,
            wins_1r=wins_1r,
            losses_1r=losses_1r,
            unresolved_1r=unresolved_1r,
            wins_2r=wins_2r,
            losses_2r=losses_2r,
            unresolved_2r=unresolved_2r,
            average_penetration=average_penetration,
            average_mfe_1r=average_mfe_1r,
            average_mae_1r=average_mae_1r,
            average_mfe_2r=average_mfe_2r,
            average_mae_2r=average_mae_2r,
        )

    return results