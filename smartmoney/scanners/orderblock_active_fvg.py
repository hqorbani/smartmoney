from smartmoney.scanners.base import Scanner
from smartmoney.models.signal import Signal
from smartmoney.models.fvg import FVGStatus


class OrderBlockActiveFVGScanner(Scanner):

    def scan(self, context):

        signals = []

        for ob in context.orderblocks:

            if ob.related_fvg is None:
                continue

            if ob.related_fvg.status != FVGStatus.ACTIVE:
                continue

            signals.append(

                Signal(

                    symbol=context.symbol,

                    timeframe=context.timeframe,

                    strategy="OB + ACTIVE_FVG",

                    direction="BUY" if ob.bullish else "SELL",

                    price_low=ob.low,

                    price_high=ob.high,

                    time=ob.time,

                    score=1.0,

                )

            )

        return signals