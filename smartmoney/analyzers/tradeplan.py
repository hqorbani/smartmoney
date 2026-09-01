from smartmoney.analyzers.base import Analyzer
from smartmoney.models.signal import SignalDirection
from smartmoney.models.tradeplan import TradePlan


class TradePlanAnalyzer(Analyzer):

    priority = 70

    def analyze(self, context):

        context.trade_plan = None

        take_profit_plan = context.take_profit_plan

        if take_profit_plan is None:
            return

        stop_loss_plan = take_profit_plan.stop_loss_plan

        if stop_loss_plan is None:
            return

        entry_plan = stop_loss_plan.entry_plan

        if entry_plan is None:
            return

        direction = context.signal.direction

        if direction not in (
            SignalDirection.BUY,
            SignalDirection.SELL,
        ):
            return

        entry_price = float(entry_plan.entry_price)
        stop_loss = float(stop_loss_plan.stop_loss)
        take_profit = float(take_profit_plan.take_profit)

        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)

        if risk <= 0:
            return

        risk_reward_ratio = reward / risk

        context.trade_plan = TradePlan(
            direction=direction,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk=risk,
            reward=reward,
            risk_reward_ratio=risk_reward_ratio,
        )