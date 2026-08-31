from dataclasses import dataclass

from smartmoney.models.entry import EntryPlan


@dataclass
class StopLossPlan:

    stop_loss: float

    entry_plan: EntryPlan

    