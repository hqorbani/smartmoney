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

            # -----------------------------
            # Bullish FVG
            # -----------------------------
            if lows[c3] > highs[c1]:

                gap_high = lows[c3]
                gap_low = highs[c1]

                if (gap_high - gap_low) >= Config.MIN_FVG_SIZE:

                    if not any(
                        fvg.start_time == times.iloc[c1]
                        and fvg.end_time == times.iloc[c3]
                        and fvg.bullish
                        for fvg in context.fvgs
                    ):
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

            # -----------------------------
            # Bearish FVG
            # -----------------------------
            elif highs[c3] < lows[c1]:

                gap_high = lows[c1]
                gap_low = highs[c3]

                if (gap_high - gap_low) >= Config.MIN_FVG_SIZE:

                    if not any(
                        fvg.start_time == times.iloc[c1]
                        and fvg.end_time == times.iloc[c3]
                        and not fvg.bullish
                        for fvg in context.fvgs
                    ):
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
        # فقط candleهای بعد از تشکیل FVG بررسی می‌شوند.
        #
        # Bullish:
        # اگر Low وارد محدوده FVG شود => MITIGATED
        #
        # Bearish:
        # اگر High وارد محدوده FVG شود => MITIGATED
        #
        # State قبلی FVG حفظ می‌شود.
        # ---------------------------------------------------------

        for fvg in context.fvgs:

            # FVGهایی که قبلاً mitigate شده‌اند را تغییر نده.
            if fvg.status == FVGStatus.MITIGATED:
                continue

            # FVGهایی که هنوز active هستند، فقط candleهای
            # بعد از candle تشکیل‌دهنده FVG را بررسی می‌کنند.
            start_index = fvg.end_index + 1

            for i in range(start_index, len(df)):

                candle_low = lows[i]
                candle_high = highs[i]

                if fvg.bullish:

                    # قیمت وارد محدوده Bullish FVG شده است.
                    if candle_low <= fvg.high:

                        fvg.status = FVGStatus.MITIGATED
                        fvg.mitigation_index = i
                        fvg.mitigation_time = times.iloc[i]

                        break

                else:

                    # قیمت وارد محدوده Bearish FVG شده است.
                    if candle_high >= fvg.low:

                        fvg.status = FVGStatus.MITIGATED
                        fvg.mitigation_index = i
                        fvg.mitigation_time = times.iloc[i]

                        break

        # if Config.PRINT_FVGS:
        #
        #     print()
        #     print(f"{context.symbol} {context.timeframe}")
        #     print(f"FVGs : {len(context.fvgs)}")
        #
        #     for fvg in context.fvgs[-10:]:
        #
        #         print(
        #             f"{'BULL' if fvg.bullish else 'BEAR'} | "
        #             f"{fvg.status.value} | "
        #             f"{fvg.low:.5f} -> {fvg.high:.5f}"
        #         )