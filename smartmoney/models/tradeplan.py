from dataclasses import dataclass

from smartmoney.models.signal import SignalDirection


@dataclass
class TradePlan:

    direction: SignalDirection

    entry_price: float

    stop_loss: float

    take_profit: float

    risk: float

    reward: float

    risk_reward_ratio: float