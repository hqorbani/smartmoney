from smartmoney.analyzers.base import Analyzer
from smartmoney.models.position_size import PositionSizePlan
from smartmoney.models.symbol_trading_info import SymbolTradingInfo


class PositionSizeAnalyzer(Analyzer):

    priority = 90

    def __init__(
        self,
        balance: float,
        risk_percent: float,
        symbol_trading_info_provider,
    ):
        self.balance = float(balance)
        self.risk_percent = float(risk_percent)
        self.symbol_trading_info_provider = symbol_trading_info_provider

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

        tick_size = symbol_trading_info.tick_size
        tick_value = symbol_trading_info.tick_value

        if tick_size <= 0 or tick_value <= 0:
            return

        stop_distance = abs(
            float(trade_plan.entry_price)
            - float(trade_plan.stop_loss)
        )

        if stop_distance <= 0:
            return

        stop_distance_ticks = stop_distance / tick_size

        risk_amount = (
            self.balance
            * self.risk_percent
            / 100.0
        )

        if risk_amount <= 0:
            return

        risk_per_lot = (
            stop_distance_ticks
            * tick_value
        )

        if risk_per_lot <= 0:
            return

        position_size = (
            risk_amount
            / risk_per_lot
        )

        context.position_size_plan = PositionSizePlan(
            balance=self.balance,
            risk_percent=self.risk_percent,
            risk_amount=risk_amount,
            stop_distance=stop_distance,
            position_size=position_size,
        )