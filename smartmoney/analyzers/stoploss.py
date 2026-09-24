from smartmoney.analyzers.base import Analyzer
from smartmoney.models.stoploss import StopLossPlan
from smartmoney.models.signal import SignalDirection


class StopLossAnalyzer(Analyzer):

    priority = 60

    def analyze(self, context):

        context.stop_loss_plan = None

        entry_plan = context.entry_plan

        if entry_plan is None:
            return

        entry_price = float(entry_plan.entry_price)
        orderblock = entry_plan.orderblock

        if context.signal.direction == SignalDirection.BUY:

            stop_loss = float(orderblock.expanded_low)

            if stop_loss >= entry_price:
                return

        elif context.signal.direction == SignalDirection.SELL:

            stop_loss = float(orderblock.expanded_high)

            if stop_loss <= entry_price:
                return

        else:
            return

        context.stop_loss_plan = StopLossPlan(
            stop_loss=stop_loss,
            entry_plan=entry_plan,
        )