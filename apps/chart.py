from smartmoney.config import Config

from smartmoney.core.context import MarketContext
from smartmoney.core.mt5 import MT5DataProvider

from smartmoney.analyzers.swing import SwingAnalyzer
from smartmoney.analyzers.fvg import FVGAnalyzer
from smartmoney.analyzers.fvg_lifecycle import FVGLifecycleAnalyzer
from smartmoney.analyzers.orderblock import OrderBlockAnalyzer

from smartmoney.visualization.chart import ChartVisualizer


def main():

    provider = MT5DataProvider()

    provider.connect()

    try:

        df = provider.fetch_rates(
            symbol=Config.SYMBOLS[0],
            timeframe=Config.TIMEFRAMES[0],
            count=Config.HISTORY_BARS,
        )

        context = MarketContext(
            symbol=Config.SYMBOLS[0],
            timeframe=Config.TIMEFRAMES[0],
            df=df,
        )

        SwingAnalyzer().analyze(context)
        FVGAnalyzer().analyze(context)
        FVGLifecycleAnalyzer().analyze(context)
        OrderBlockAnalyzer().analyze(context)

        ChartVisualizer().show(context)

    finally:

        provider.shutdown()


if __name__ == "__main__":
    main()