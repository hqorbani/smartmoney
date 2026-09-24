import pandas as pd

from smartmoney.analyzers.base import Analyzer
from smartmoney.config import Config
from smartmoney.models.orderblock import OrderBlock
from smartmoney.services.atr_service import ATRService


class OrderBlockAnalyzer(Analyzer):
    priority = 30

    def analyze(self, context):
        df = context.df

        atr_series = ATRService().calculate(
            df,
            Config.ATR_PERIOD,
        )

        opens = df["open"].to_numpy()
        highs = df["high"].to_numpy()
        lows = df["low"].to_numpy()
        closes = df["close"].to_numpy()
        times = df["time"]

        # جلوگیری از ایجاد OrderBlock تکراری
        used_indexes = set()

        for fvg in context.fvgs:

            # کندل وسط FVG (Impulse Candle)
            impulse_index = fvg.start_index + 1

            if fvg.bullish:

                # آخرین کندل نزولی قبل از Impulse
                for i in range(impulse_index - 1, -1, -1):

                    if closes[i] < opens[i]:

                        if i not in used_indexes:

                            # اگر این Bullish OB قبلاً ساخته شده،
                            # همان OB را حفظ می‌کنیم.
                            if any(
                                ob.index == i and ob.bullish is True
                                for ob in context.orderblocks
                            ):
                                break

                            atr_ob = atr_series.iloc[i]

                            if pd.notna(atr_ob):
                                expansion = (
                                    atr_ob * Config.OB_EXPANSION_FACTOR
                                )
                                expanded_high = highs[i] + expansion
                                expanded_low = lows[i] - expansion
                            else:
                                expanded_high = None
                                expanded_low = None

                            context.orderblocks.append(
                                OrderBlock(
                                    index=i,
                                    time=times.iloc[i],
                                    open=opens[i],
                                    high=highs[i],
                                    low=lows[i],
                                    close=closes[i],
                                    bullish=True,
                                    expanded_high=expanded_high,
                                    expanded_low=expanded_low,
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

                            # اگر این Bearish OB قبلاً ساخته شده،
                            # همان OB را حفظ می‌کنیم.
                            if any(
                                ob.index == i and ob.bullish is False
                                for ob in context.orderblocks
                            ):
                                break

                            atr_ob = atr_series.iloc[i]

                            if pd.notna(atr_ob):
                                expansion = (
                                    atr_ob * Config.OB_EXPANSION_FACTOR
                                )
                                expanded_high = highs[i] + expansion
                                expanded_low = lows[i] - expansion
                            else:
                                expanded_high = None
                                expanded_low = None

                            context.orderblocks.append(
                                OrderBlock(
                                    index=i,
                                    time=times.iloc[i],
                                    open=opens[i],
                                    high=highs[i],
                                    low=lows[i],
                                    close=closes[i],
                                    bullish=False,
                                    expanded_high=expanded_high,
                                    expanded_low=expanded_low,
                                    related_fvg=fvg,
                                )
                            )

                            used_indexes.add(i)

                        break

        # ---------------------------------------------------------
        # OrderBlock Mitigation
        # ---------------------------------------------------------
        #
        # Bullish OB:
        # اگر Low یک کندل بعد از OB وارد محدوده OB شود،
        # OB می‌شود mitigated.
        #
        # Bearish OB:
        # اگر High یک کندل بعد از OB وارد محدوده OB شود،
        # OB می‌شود mitigated.
        #
        # candle خود OB بررسی نمی‌شود.
        # بررسی از candle بعد از OB شروع می‌شود.
        #
        # اگر OB قبلاً mitigated شده باشد، state آن حفظ می‌شود
        # و دوباره محاسبه نمی‌شود.

        for ob in context.orderblocks:

            if ob.mitigated:
                continue

            # Mitigation فقط بعد از تشکیل FVG مربوط به OB
            start_index = ob.related_fvg.end_index + 1

            for i in range(start_index, len(df) - 1):

                candle_low = lows[i]
                candle_high = highs[i]

                if ob.expanded_high is None or ob.expanded_low is None:
                    continue

                if ob.bullish:
                    if candle_low <= ob.expanded_high:
                        ob.mitigated = True
                        ob.mitigation_index = i
                        ob.mitigation_time = times.iloc[i]
                        break

                else:
                    if candle_high >= ob.expanded_low:
                        ob.mitigated = True
                        ob.mitigation_index = i
                        ob.mitigation_time = times.iloc[i]
                        break