from smartmoney.analyzers.base import Analyzer
from smartmoney.models.entry import EntryPlan, EntryZone
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

        if (
            orderblock.expanded_high is None
            or orderblock.expanded_low is None
        ):
            return

        ob_high = float(orderblock.expanded_high)
        ob_low = float(orderblock.expanded_low)

        if ob_low >= ob_high:
            return

        entry_zone = EntryZone(
            name="ENTRY",
            price_low=ob_low,
            price_high=ob_high,
        )

        if signal.direction == SignalDirection.BUY:
            entry_price = ob_high
        elif signal.direction == SignalDirection.SELL:
            entry_price = ob_low
        else:
            return

        context.entry_plan = EntryPlan(
            entry_price=entry_price,
            orderblock=orderblock,
            fvg=signal.fvg,
            zones=[entry_zone],
        )
