from smartmoney.analyzers.base import Analyzer
from smartmoney.models.signal import Signal, SignalDirection


class SignalAnalyzer(Analyzer):

    priority = 40

    def analyze(self, context):

        context.signal = Signal()

        if not context.fvgs or not context.orderblocks:
            return

        for ob in context.orderblocks:

            if ob.mitigated:
                continue

            fvg = ob.related_fvg

            if fvg is None:
                continue

            if ob.bullish != fvg.bullish:
                continue

            if ob.bullish:

                context.signal = Signal(
                    direction=SignalDirection.BUY,
                    reason="bullish_orderblock_with_bullish_fvg",
                    orderblock=ob,
                    fvg=fvg,
                )

                return

            context.signal = Signal(
                direction=SignalDirection.SELL,
                reason="bearish_orderblock_with_bearish_fvg",
                orderblock=ob,
                fvg=fvg,
            )

            return