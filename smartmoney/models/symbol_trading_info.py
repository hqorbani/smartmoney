from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SymbolTradingInfo:
    tick_size: float
    tick_value: float
    contract_size: float
    digits: int
    volume_min: float
    volume_max: float
    volume_step: float