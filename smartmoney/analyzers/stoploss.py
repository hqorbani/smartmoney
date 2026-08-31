from smartmoney.analyzers.base import Analyzer
from smartmoney.models.stoploss import StopLossPlan
from smartmoney.models.signal import SignalDirection


class StopLossAnalyzer(Analyzer):

    priority = 50

    def analyze(self, context):

        context.stop_loss_plan = None

        entry_plan = context.entry_plan

        if entry_plan is None:
            return

        orderblock = entry_plan.orderblock

        if context.signal.direction == SignalDirection.BUY:

            stop_loss = float(orderblock.low)

        elif context.signal.direction == SignalDirection.SELL:

            stop_loss = float(orderblock.high)

        else:
            return

        context.stop_loss_plan = StopLossPlan(
            stop_loss=stop_loss,
            entry_plan=entry_plan,
        )