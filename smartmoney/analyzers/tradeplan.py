from smartmoney.analyzers.base import Analyzer
from smartmoney.models.signal import SignalDirection
from smartmoney.trading.trade_plan import TradeDirection, TradePlan


class TradePlanAnalyzer(Analyzer):

    priority = 80

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

        stop_loss = float(stop_loss_plan.stop_loss)
        take_profit = float(take_profit_plan.take_profit)

        if direction == SignalDirection.BUY:
            if context.current_ask is None:
                return
            entry_price = float(context.current_ask)

        elif direction == SignalDirection.SELL:
            if context.current_bid is None:
                return
            entry_price = float(context.current_bid)

        else:
            return
        
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        
        if risk <= 0:
            return
        risk_reward_ratio = reward / risk
        trade_direction = (
            TradeDirection.BUY
            if direction == SignalDirection.BUY
            else TradeDirection.SELL
        )

        context.trade_plan = TradePlan(
            symbol=context.symbol,
            timeframe=context.timeframe,
            direction=trade_direction,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_distance=risk,
            orderblock_index=0,
        )