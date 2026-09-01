from smartmoney.analyzers.entry import EntryAnalyzer
from smartmoney.analyzers.fvg import FVGAnalyzer
from smartmoney.analyzers.orderblock import OrderBlockAnalyzer
from smartmoney.analyzers.position_size import PositionSizeAnalyzer
from smartmoney.analyzers.signal import SignalAnalyzer
from smartmoney.analyzers.stoploss import StopLossAnalyzer
from smartmoney.analyzers.takeprofit import TakeProfitAnalyzer
from smartmoney.analyzers.tradeplan import TradePlanAnalyzer


def test_analyzer_priorities_follow_trade_pipeline():
    assert FVGAnalyzer.priority < OrderBlockAnalyzer.priority
    assert OrderBlockAnalyzer.priority < SignalAnalyzer.priority
    assert SignalAnalyzer.priority < EntryAnalyzer.priority
    assert EntryAnalyzer.priority < StopLossAnalyzer.priority
    assert StopLossAnalyzer.priority < TakeProfitAnalyzer.priority
    assert TakeProfitAnalyzer.priority < TradePlanAnalyzer.priority
    assert TradePlanAnalyzer.priority < PositionSizeAnalyzer.priority