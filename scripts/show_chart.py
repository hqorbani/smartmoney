from smartmoney.config import Config

from smartmoney.analyzers.swing import SwingAnalyzer
from smartmoney.core.context import MarketContext
from smartmoney.core.mt5 import MT5DataProvider
from smartmoney.visualization.chart import ChartVisualizer


def main() -> None:
    provider = MT5DataProvider()

    provider.connect()

    try:
        timeframe = Config.TIMEFRAMES[0]

        df = provider.fetch_rates(
            "EURUSD",
            timeframe,
            Config.HISTORY_BARS,
        )

        context = MarketContext(
            symbol="EURUSD",
            timeframe=timeframe,
            df=df,
        )

        SwingAnalyzer().analyze(context)

        ChartVisualizer().show(context)

    finally:
        provider.shutdown()


if __name__ == "__main__":
    main()