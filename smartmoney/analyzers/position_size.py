import math
from smartmoney.analyzers.base import Analyzer
from smartmoney.models.position_size import PositionSizePlan


class PositionSizeAnalyzer(Analyzer):

    priority = 90

    def __init__(
        self,
        balance: float,
        risk_percent: float,
        symbol_trading_info_provider,
        loss_per_lot_provider,
    ):
        self.balance = float(balance)
        self.risk_percent = float(risk_percent)
        self.symbol_trading_info_provider = symbol_trading_info_provider
        self.loss_per_lot_provider = loss_per_lot_provider

    def analyze(self, context):

        context.position_size_plan = None

        trade_plan = context.trade_plan

        if trade_plan is None:
            return

        if self.balance <= 0:
            return

        if self.risk_percent <= 0 or self.risk_percent > 100:
            return

        symbol_trading_info = self.symbol_trading_info_provider(
            context.symbol
        )

        stop_distance = abs(
            float(trade_plan.entry_price)
            - float(trade_plan.stop_loss)
        )

        if stop_distance <= 0:
            return

        risk_amount = (
            self.balance
            * self.risk_percent
            / 100.0
        )

        if risk_amount <= 0:
            return
        risk_per_lot = self.loss_per_lot_provider(
            context.symbol,
            trade_plan.direction,
            float(trade_plan.entry_price),
            float(trade_plan.stop_loss),
        )

        if risk_per_lot is None:
            return

        if (
            not math.isfinite(risk_per_lot)
            or risk_per_lot <= 0
        ):
            return

        if risk_per_lot <= 0:
            return

        position_size = (
            risk_amount
            / risk_per_lot
        )

        if not math.isfinite(position_size):
            return
        volume_min = symbol_trading_info.volume_min
        volume_max = symbol_trading_info.volume_max
        volume_step = symbol_trading_info.volume_step

        if volume_min <= 0 or volume_max <= 0 or volume_step <= 0:
            return

        if position_size < volume_min:
            position_size = volume_min
        else:
            position_size = (
                int(position_size / volume_step)
                * volume_step
            )

        if position_size > volume_max:
            position_size = volume_max

        context.position_size_plan = PositionSizePlan(
            balance=self.balance,
            risk_percent=self.risk_percent,
            risk_amount=risk_amount,
            stop_distance=stop_distance,
            position_size=position_size,
        )