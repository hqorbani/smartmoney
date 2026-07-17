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

            fvg.status = FVGStatus.ACTIVE
            fvg.mitigation_index = None
            fvg.mitigation_time = None

            for i in range(fvg.end_index + 1, len(df)):

                if fvg.bullish:

                    # اولین ورود قیمت به Gap
                    if (
                        fvg.status == FVGStatus.ACTIVE
                        and lows[i] <= fvg.high
                    ):

                        fvg.status = FVGStatus.MITIGATED
                        fvg.mitigation_index = i
                        fvg.mitigation_time = times.iloc[i]

                    # پر شدن کامل Gap
                    if lows[i] <= fvg.low:

                        fvg.status = FVGStatus.FILLED

                        break

                else:

                    # اولین ورود قیمت به Gap
                    if (
                        fvg.status == FVGStatus.ACTIVE
                        and highs[i] >= fvg.low
                    ):

                        fvg.status = FVGStatus.MITIGATED
                        fvg.mitigation_index = i
                        fvg.mitigation_time = times.iloc[i]

                    # پر شدن کامل Gap
                    if highs[i] >= fvg.high:

                        fvg.status = FVGStatus.FILLED

                        break