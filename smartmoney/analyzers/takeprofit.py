from smartmoney.analyzers.base import Analyzer
from smartmoney.config import Config
from smartmoney.models.signal import SignalDirection
from smartmoney.models.takeprofit import TakeProfitPlan


class TakeProfitAnalyzer(Analyzer):

    priority = 60

    def analyze(self, context):

        context.take_profit_plan = None

        stop_loss_plan = context.stop_loss_plan

        if stop_loss_plan is None:
            return

        entry_plan = stop_loss_plan.entry_plan

        entry_price = float(entry_plan.entry_price)
        stop_loss = float(stop_loss_plan.stop_loss)

        risk = abs(entry_price - stop_loss)

        if risk <= 0:
            return

        rr_ratio = float(Config.RR_RATIO)

        if rr_ratio <= 0:
            return

        if context.signal.direction == SignalDirection.BUY:

            take_profit = entry_price + (risk * rr_ratio)

        elif context.signal.direction == SignalDirection.SELL:

            take_profit = entry_price - (risk * rr_ratio)

        else:
            return

        context.take_profit_plan = TakeProfitPlan(
            take_profit=take_profit,
            stop_loss_plan=stop_loss_plan,
        )