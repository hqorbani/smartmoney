from smartmoney.analyzers.base import Analyzer
from smartmoney.models.position_size import PositionSizePlan


class PositionSizeAnalyzer(Analyzer):

    priority = 90

    def __init__(
        self,
        balance: float,
        risk_percent: float,
        pip_size: float,
        pip_value: float,
    ):
        self.balance = float(balance)
        self.risk_percent = float(risk_percent)
        self.pip_size = float(pip_size)
        self.pip_value = float(pip_value)

    def analyze(self, context):

        context.position_size_plan = None

        trade_plan = context.trade_plan

        if trade_plan is None:
            return
        if self.balance <= 0:
            return

        if self.risk_percent <= 0 or self.risk_percent > 100:
            return

        pip_size = self.pip_size
        pip_value = self.pip_value

        if pip_size <= 0 or pip_value <= 0:
            return

        stop_distance = abs(
            float(trade_plan.entry_price)
            - float(trade_plan.stop_loss)
        )

        if stop_distance <= 0:
            return

        stop_distance_pips = stop_distance / pip_size

        risk_amount = (
            self.balance
            * self.risk_percent
            / 100.0
        )

        if risk_amount <= 0:
            return

        risk_per_lot = (
            stop_distance_pips
            * pip_value
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