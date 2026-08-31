from dataclasses import dataclass

from smartmoney.models.stoploss import StopLossPlan


@dataclass
class TakeProfitPlan:

    take_profit: float

    stop_loss_plan: StopLossPlan