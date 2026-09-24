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

        if orderblock.expanded_high is None or orderblock.expanded_low is None:
            return

        ob_high = float(orderblock.expanded_high)
        ob_low = float(orderblock.expanded_low)

        zone_size = (ob_high - ob_low) / 3.0

        if signal.direction == SignalDirection.BUY:

            initial_zone = EntryZone(
                name="INITIAL",
                price_low=ob_low,
                price_high=ob_low + zone_size,
            )

            middle_zone = EntryZone(
                name="MIDDLE",
                price_low=ob_low + zone_size,
                price_high=ob_low + (zone_size * 2),
            )

            final_zone = EntryZone(
                name="FINAL",
                price_low=ob_low + (zone_size * 2),
                price_high=ob_high,
            )

        else:

            initial_zone = EntryZone(
                name="INITIAL",
                price_low=ob_high - zone_size,
                price_high=ob_high,
            )

            middle_zone = EntryZone(
                name="MIDDLE",
                price_low=ob_high - (zone_size * 2),
                price_high=ob_high - zone_size,
            )

            final_zone = EntryZone(
                name="FINAL",
                price_low=ob_low,
                price_high=ob_high - (zone_size * 2),
            )

        entry_price = (ob_high + ob_low) / 2.0

        context.entry_plan = EntryPlan(
            entry_price=entry_price,
            orderblock=orderblock,
            fvg=signal.fvg,
            zones=[
                initial_zone,
                middle_zone,
                final_zone,
            ],
        )