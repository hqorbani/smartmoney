from smartmoney.scanners.base import Scanner
from smartmoney.models.signal import Signal
from smartmoney.models.fvg import FVGStatus
from smartmoney.models.orderblock import (
    Attempt1Status,
    Attempt2Status,
)

class OrderBlockActiveFVGScanner(Scanner):

    def scan(self, context):

        signals = []

        for ob in context.orderblocks:

            if ob.related_fvg is None:
                continue

            if ob.related_fvg.status != FVGStatus.ACTIVE:
                continue

            if ob.mitigated:
                continue

            if ob.expanded_low is None or ob.expanded_high is None:
                continue

            if context.current_bid is None or context.current_ask is None:
                continue

            if (
                ob.attempt1_status != Attempt1Status.NOT_USED
                and ob.attempt2_status != Attempt2Status.AVAILABLE
            ):
                continue

            signals.append(

                Signal(
                    symbol=context.symbol,
                    timeframe=context.timeframe,
                    strategy="OB + ACTIVE_FVG",
                    signal_id=(
                        f"{context.symbol}|{context.timeframe}|OB + ACTIVE_FVG|"
                        f"{'BUY' if ob.bullish else 'SELL'}|{ob.time.isoformat()}"
                    ),
                    direction="BUY" if ob.bullish else "SELL",
                    price_low=ob.expanded_low,
                    price_high=ob.expanded_high,
                    time=ob.time,
                    score=1.0,
                    orderblock=ob,
                    fvg=ob.related_fvg,
                )

            )

        return signals