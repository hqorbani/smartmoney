from smartmoney.analyzers.base import Analyzer
from smartmoney.models.fvg import FVGStatus


class FVGLifecycleAnalyzer(Analyzer):

    priority = 21

    def analyze(self, context):

        df = context.df

        highs = df["high"].to_numpy()
        lows = df["low"].to_numpy()
        times = df["time"]

        for fvg in context.fvgs:

            # Filled is terminal.
            if fvg.status == FVGStatus.FILLED:
                continue

            for i in range(fvg.end_index + 1, len(df)):

                # -------------------------------------------------
                # Bullish FVG
                # -------------------------------------------------

                if fvg.bullish:

                    # Full fill has priority over mitigation.
                    if lows[i] <= fvg.low:

                        fvg.status = FVGStatus.FILLED
                        fvg.fill_index = i
                        fvg.fill_time = times.iloc[i]

                        break

                    # First entry into the FVG zone.
                    if (
                        fvg.status == FVGStatus.ACTIVE
                        and lows[i] <= fvg.high
                    ):

                        fvg.status = FVGStatus.MITIGATED
                        fvg.mitigation_index = i
                        fvg.mitigation_time = times.iloc[i]

                # -------------------------------------------------
                # Bearish FVG
                # -------------------------------------------------

                else:

                    # Full fill has priority over mitigation.
                    if highs[i] >= fvg.high:

                        fvg.status = FVGStatus.FILLED
                        fvg.fill_index = i
                        fvg.fill_time = times.iloc[i]

                        break

                    # First entry into the FVG zone.
                    if (
                        fvg.status == FVGStatus.ACTIVE
                        and highs[i] >= fvg.low
                    ):

                        fvg.status = FVGStatus.MITIGATED
                        fvg.mitigation_index = i
                        fvg.mitigation_time = times.iloc[i]