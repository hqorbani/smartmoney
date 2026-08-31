from smartmoney.config import Config
from smartmoney.analyzers.base import Analyzer
from smartmoney.models.fvg import FVG


class FVGAnalyzer(Analyzer):

    priority = 20

    def analyze(self, context):


        df = context.df

        highs = df["high"].to_numpy()
        lows = df["low"].to_numpy()
        times = df["time"]

        if len(df) < 3:
            return

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

                    context.fvgs.append(

                        

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
                    

        # if Config.PRINT_FVGS:
        #     print()
        #     print(f"{context.symbol} {context.timeframe}")
        #     print(f"FVGs : {len(context.fvgs)}")

        #     for fvg in context.fvgs[-10:]:

        #         print(
        #             f"{'BULL' if fvg.bullish else 'BEAR'} | "
        #             f"{fvg.status.value} | "
        #             f"{fvg.low:.5f} -> {fvg.high:.5f}"
        #         )