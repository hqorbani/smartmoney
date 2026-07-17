from smartmoney.models.fvg import FVGStatus
from smartmoney.models.signal import Signal

from smartmoney.scanners.base import Scanner


class ActiveFVGScanner(Scanner):

    def scan(self, context):

        signals = []

        for fvg in context.fvgs:

            if fvg.status != FVGStatus.ACTIVE:
                continue

            signals.append(

                Signal(

                    symbol=context.symbol,

                    timeframe=context.timeframe,

                    strategy="ACTIVE_FVG",

                    direction="BUY" if fvg.bullish else "SELL",

                    price_low=fvg.low,

                    price_high=fvg.high,

                    time=fvg.start_time,

                )

            )

        return signals