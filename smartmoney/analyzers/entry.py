from smartmoney.analyzers.base import Analyzer
from smartmoney.models.entry import EntryPlan
from smartmoney.models.signal import SignalDirection


class EntryAnalyzer(Analyzer):

    priority = 50

    def analyze(self, context):

        context.entry_plan = None

        signal = context.signal

        if signal.direction == SignalDirection.NO_SIGNAL:
            return

        if signal.orderblock is None:
            return

        if signal.fvg is None:
            return

        if context.df.empty:
            return

        orderblock = signal.orderblock

        

        if orderblock.expanded_high is None or orderblock.expanded_low is None:
            return

        ob_high = float(orderblock.expanded_high)
        ob_low = float(orderblock.expanded_low)

        entry_price = (ob_high + ob_low) / 2.0

        context.entry_plan = EntryPlan(
            entry_price=entry_price,
            orderblock=orderblock,
            fvg=signal.fvg,
        )