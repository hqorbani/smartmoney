from smartmoney.config import Config
from smartmoney.models.orderblock import (
    Attempt1Status,
    Attempt2Status,
    OrderBlockStatus,
)
from smartmoney.scoring.base import ScoreRule
from smartmoney.models.signal import SignalDirection

class OrderBlockEntryReadinessScore(ScoreRule):
    def score(self, signal, context):
        orderblock = signal.orderblock
        entry_plan = getattr(context, "entry_plan", None)

        if orderblock is None or entry_plan is None:
            return 0.0

        if orderblock.status != OrderBlockStatus.ACTIVE:
            return 0.0

        if signal.direction == SignalDirection.BUY:
            execution_price = context.current_ask
        elif signal.direction == SignalDirection.SELL:
            execution_price = context.current_bid
        else:
            return 0.0

        if execution_price is None:
            return 0.0

        entry_zone = next(
            (
                zone
                for zone in entry_plan.zones
                if zone.name == "ENTRY"
            ),
            None,
        )

        if entry_zone is None:
            return 0.0

        inside_entry = (
            entry_zone.price_low
            <= execution_price
            <= entry_zone.price_high
        )

        if not inside_entry:
            return 0.0

        if orderblock.attempt1_status == Attempt1Status.NOT_USED:
            return Config.ORDER_BLOCK_ENTRY_READINESS_SCORE

        if (
            orderblock.attempt1_status == Attempt1Status.FAILED
            and orderblock.attempt2_status == Attempt2Status.AVAILABLE
        ):
            return Config.ORDER_BLOCK_ENTRY_READINESS_SCORE

        return 0.0