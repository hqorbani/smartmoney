from smartmoney.bootstrap import create_chart_context
from smartmoney.config import Config
from smartmoney.visualization.chart import ChartVisualizer


def main():

    context = create_chart_context(
        symbol=Config.SYMBOLS[5],
        timeframe=Config.TIMEFRAMES[0],
    )

    ChartVisualizer().show(context)


if __name__ == "__main__":
    main()