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

        last_candle = context.df.iloc[-1]

        candle_high = float(last_candle["high"])
        candle_low = float(last_candle["low"])

        ob_high = float(orderblock.high)
        ob_low = float(orderblock.low)

        # Price has not reached the Order Block.
        if candle_high < ob_low or candle_low > ob_high:
            return

        entry_price = (ob_high + ob_low) / 2.0

        context.entry_plan = EntryPlan(
            entry_price=entry_price,
            orderblock=orderblock,
            fvg=signal.fvg,
        )