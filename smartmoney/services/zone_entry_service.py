from dataclasses import dataclass


@dataclass
class ZoneEntryState:
    inside: bool = False


class ZoneEntryService:
    def is_first_entry(
        self,
        state: ZoneEntryState,
        price: float,
        price_low: float,
        price_high: float,
    ) -> bool:
        inside = price_low <= price <= price_high

        if not inside:
            state.inside = False
            return False

        if state.inside:
            return False

        state.inside = True
        return True