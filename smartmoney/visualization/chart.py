import plotly.graph_objects as go

from smartmoney.core.context import MarketContext
from smartmoney.models.fvg import FVGStatus


class ChartVisualizer:

    def show(self, context: MarketContext):

        df = context.df

        fig = go.Figure()

        # ==================================================
        # Candles
        # ==================================================

        fig.add_trace(
            go.Candlestick(
                x=df["time"],
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
                name=context.symbol,
            )
        )

        # ==================================================
        # Swings
        # ==================================================

        swing_high_x = []
        swing_high_y = []

        swing_low_x = []
        swing_low_y = []

        for swing in context.swings:

            if swing.is_high:

                swing_high_x.append(swing.time)
                swing_high_y.append(swing.price)

            else:

                swing_low_x.append(swing.time)
                swing_low_y.append(swing.price)

        fig.add_trace(
            go.Scatter(
                x=swing_high_x,
                y=swing_high_y,
                mode="markers",
                name="Swing High",
                marker=dict(
                    symbol="triangle-down",
                    size=12,
                ),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=swing_low_x,
                y=swing_low_y,
                mode="markers",
                name="Swing Low",
                marker=dict(
                    symbol="triangle-up",
                    size=12,
                ),
            )
        )

        # ==================================================
        # FVG
        # ==================================================

        for fvg in context.fvgs:

            # FVG پر شده دیگر رسم نشود
            if fvg.status == FVGStatus.FILLED:
                continue

            if fvg.bullish:

                color = (
                    "rgba(0,200,0,0.30)"
                    if fvg.status == FVGStatus.ACTIVE
                    else "rgba(0,200,0,0.12)"
                )

            else:

                color = (
                    "rgba(220,0,0,0.30)"
                    if fvg.status == FVGStatus.ACTIVE
                    else "rgba(220,0,0,0.12)"
                )

            if fvg.status == FVGStatus.ACTIVE:

                x1 = df["time"].iloc[-1]

            else:

                x1 = fvg.mitigation_time

            fig.add_shape(

                type="rect",

                x0=fvg.start_time,
                x1=x1,

                y0=fvg.low,
                y1=fvg.high,

                fillcolor=color,

                line=dict(
                    color=color,
                    width=1,
                ),

                layer="below",

            )

        # ==================================================
        # Order Blocks
        # ==================================================

        for ob in context.orderblocks:

            color = (
                "rgba(30,144,255,0.25)"
                if ob.bullish
                else "rgba(255,140,0,0.25)"
            )

            fig.add_shape(

                type="rect",

                x0=ob.time,
                x1=df["time"].iloc[-1],

                y0=ob.low,
                y1=ob.high,

                fillcolor=color,

                line=dict(
                    color=color,
                    width=2,
                ),

                layer="below",

            )

        # ==================================================
        # Layout
        # ==================================================

        fig.update_layout(

            title=f"{context.symbol} - TF {context.timeframe}",

            template="plotly_dark",

            showlegend=False,

            xaxis_rangeslider_visible=False,

            dragmode="pan",
        )

        fig.show()