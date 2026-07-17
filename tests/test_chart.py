from smartmoney import config

from smartmoney.analyzers.swing import SwingAnalyzer
from smartmoney.core.context import MarketContext
from smartmoney.core.mt5 import MT5DataProvider
from smartmoney.visualization.chart import ChartVisualizer


provider = MT5DataProvider()

provider.connect()

df = provider.fetch_rates(

    "EURUSD",

    config.TIMEFRAMES[0],

    config.CANDLE_COUNT,

)

context = MarketContext(

    symbol="EURUSD",

    timeframe=config.TIMEFRAMES[0],

    df=df,

)

SwingAnalyzer().analyze(context)

ChartVisualizer().show(context)

provider.shutdown()