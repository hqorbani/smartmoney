from smartmoney.config import Config
from smartmoney.analyzers.base import Analyzer
from smartmoney.models.swing import Swing


class SwingAnalyzer(Analyzer):

    priority = 10

    def analyze(self, context):

        context.swings.clear()

        df = context.df

        left = Config.SWING_LEFT
        right = Config.SWING_RIGHT

        highs = df["high"].to_numpy()
        lows = df["low"].to_numpy()
        times = df["time"]

        for i in range(left, len(df) - right):

            high = highs[i]
            low = lows[i]

            # Swing High
            if (
                high > highs[i-left:i].max()
                and
                high > highs[i+1:i+right+1].max()
            ):

                context.swings.append(
                    Swing(
                        index=i,
                        time=times.iloc[i],
                        price=high,
                        is_high=True,
                    )
                )

            # Swing Low
            elif (
                low < lows[i-left:i].min()
                and
                low < lows[i+1:i+right+1].min()
            ):

                context.swings.append(
                    Swing(
                        index=i,
                        time=times.iloc[i],
                        price=low,
                        is_high=False,
                    )
                )
        if Config.PRINT_SWINGS:

            print('----*****--------')
            print(f"{context.symbol} {context.timeframe}")
            print(f"Swings : {len(context.swings)}")

            for swing in context.swings[-10:]:

                print(
                    f"{'HIGH' if swing.is_high else 'LOW '} | "
                    f"{swing.time} | "
                    f"{swing.price:.5f}"
                )
