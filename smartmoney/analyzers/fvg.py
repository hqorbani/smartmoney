from smartmoney.config import Config
from smartmoney.analyzers.base import Analyzer
from smartmoney.models.fvg import FVG, FVGStatus


class FVGAnalyzer(Analyzer):

    priority = 20

    def analyze(self, context):

        df = context.df

        highs = df["high"].to_numpy()
        lows = df["low"].to_numpy()
        times = df["time"]

        if len(df) < 3:
            return

        # ---------------------------------------------------------
        # FVG Detection
        # ---------------------------------------------------------

        for i in range(2, len(df)):

            c1 = i - 2
            c3 = i

            # -----------------------------------------------------
            # Bullish FVG
            # -----------------------------------------------------

            if lows[c3] > highs[c1]:

                gap_high = lows[c3]
                gap_low = highs[c1]

                if (gap_high - gap_low) >= Config.MIN_FVG_SIZE:

                    exists = any(
                        fvg.start_time == times.iloc[c1]
                        and fvg.end_time == times.iloc[c3]
                        and fvg.bullish
                        for fvg in context.fvgs
                    )

                    if not exists:

                        context.fvgs.append(
                            FVG(
                                start_index=c1,
                                end_index=c3,
                                start_time=times.iloc[c1],
                                end_time=times.iloc[c3],
                                high=gap_high,
                                low=gap_low,
                                bullish=True,
                            )
                        )

            # -----------------------------------------------------
            # Bearish FVG
            # -----------------------------------------------------

            elif highs[c3] < lows[c1]:

                gap_high = lows[c1]
                gap_low = highs[c3]

                if (gap_high - gap_low) >= Config.MIN_FVG_SIZE:

                    exists = any(
                        fvg.start_time == times.iloc[c1]
                        and fvg.end_time == times.iloc[c3]
                        and not fvg.bullish
                        for fvg in context.fvgs
                    )

                    if not exists:

                        context.fvgs.append(
                            FVG(
                                start_index=c1,
                                end_index=c3,
                                start_time=times.iloc[c1],
                                end_time=times.iloc[c3],
                                high=gap_high,
                                low=gap_low,
                                bullish=False,
                            )
                        )

        # ---------------------------------------------------------
        # FVG Mitigation
        # ---------------------------------------------------------
        #
        # IMPORTANT:
        #
        # FVGAnalyzer فقط مسئول:
        #
        #     ACTIVE -> MITIGATED
        #
        # است.
        #
        # تبدیل:
        #
        #     MITIGATED -> FILLED
        #
        # توسط FVGLifecycleAnalyzer انجام می‌شود.
        #
        # بنابراین حتی اگر یک candle تا انتهای Gap نفوذ کند،
        # این analyzer فقط اولین ورود به Zone را ثبت می‌کند.
        # ---------------------------------------------------------

        for fvg in context.fvgs:
            if fvg.status == FVGStatus.FILLED:
                continue

            for i in range(fvg.end_index + 1, len(df)):
                candle_low = lows[i]
                candle_high = highs[i]

                if fvg.bullish:
                    if (
                        fvg.status == FVGStatus.ACTIVE
                        and candle_low <= fvg.high
                    ):
                        fvg.status = FVGStatus.MITIGATED
                        fvg.mitigation_index = i
                        fvg.mitigation_time = times.iloc[i]

                else:
                    if (
                        fvg.status == FVGStatus.ACTIVE
                        and candle_high >= fvg.low
                    ):
                        fvg.status = FVGStatus.MITIGATED
                        fvg.mitigation_index = i
                        fvg.mitigation_time = times.iloc[i]