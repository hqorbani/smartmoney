from smartmoney.analyzers.base import Analyzer
from smartmoney.models.orderblock import OrderBlock
from smartmoney.config import Config

class OrderBlockAnalyzer(Analyzer):

    priority = 30

    def analyze(self, context):

        context.orderblocks.clear()

        df = context.df

        opens = df["open"].to_numpy()
        highs = df["high"].to_numpy()
        lows = df["low"].to_numpy()
        closes = df["close"].to_numpy()
        times = df["time"]

        # جلوگیری از OrderBlock تکراری
        used_indexes = set()

        for fvg in context.fvgs:

            # کندل وسط FVG (Impulse Candle)
            impulse_index = fvg.start_index + 1

            if fvg.bullish:

                # آخرین کندل نزولی قبل از Impulse
                for i in range(impulse_index - 1, -1, -1):

                    if closes[i] < opens[i]:

                        if i not in used_indexes:

                            context.orderblocks.append(

                                OrderBlock(

                                    index=i,

                                    time=times.iloc[i],

                                    open=opens[i],
                                    high=highs[i],
                                    low=lows[i],
                                    close=closes[i],

                                    bullish=True,

                                    related_fvg=fvg,

                                )

                            )

                            used_indexes.add(i)

                        break

            else:

                # آخرین کندل صعودی قبل از Impulse
                for i in range(impulse_index - 1, -1, -1):

                    if closes[i] > opens[i]:

                        if i not in used_indexes:

                            context.orderblocks.append(

                                OrderBlock(

                                    index=i,

                                    time=times.iloc[i],

                                    open=opens[i],
                                    high=highs[i],
                                    low=lows[i],
                                    close=closes[i],

                                    bullish=False,

                                    related_fvg=fvg,

                                )

                            )

                            used_indexes.add(i)

                        break

        if Config.PRINT_ORDERBLOCKS:

            print()
            print(f"{context.symbol} {context.timeframe}")
            print(f"OrderBlocks : {len(context.orderblocks)}")

            for ob in context.orderblocks[-10:]:

                print(
                    f"{'BULL' if ob.bullish else 'BEAR'} | "
                    f"{ob.time} | "
                    f"{ob.low:.5f} -> {ob.high:.5f}"
                )