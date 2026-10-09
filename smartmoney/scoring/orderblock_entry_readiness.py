
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

        entry_plan = getattr(signal, "entry_plan", None)
        if entry_plan is None:
            entry_plan = getattr(context, "entry_plan", None)

        if orderblock is None or entry_plan is None:
            return 0.0

        if orderblock.status != OrderBlockStatus.ACTIVE:
            return 0.0

        direction = signal.direction
        if isinstance(direction, SignalDirection):
            direction = direction.name
        elif isinstance(direction, str):
            direction = direction.upper()

        if direction == "BUY":
            execution_price = getattr(context, "current_ask", None)
        elif direction == "SELL":
            execution_price = getattr(context, "current_bid", None)
        else:
            return 0.0

        if execution_price is None:
            return 0.0

        entry_zone = next(
            (zone for zone in entry_plan.zones if zone.name == "ENTRY"),
            None,
        )
        if entry_zone is None:
            return 0.0

        if not entry_zone.price_low <= execution_price <= entry_zone.price_high:
            return 0.0

        attempt1_ready = (
            orderblock.attempt1_status == Attempt1Status.NOT_USED
        )
        attempt2_ready = (
            orderblock.attempt1_status == Attempt1Status.FAILED
            and orderblock.attempt2_status == Attempt2Status.AVAILABLE
        )

        if attempt1_ready or attempt2_ready:
            return Config.ORDER_BLOCK_ENTRY_READINESS_SCORE

        return 0.0