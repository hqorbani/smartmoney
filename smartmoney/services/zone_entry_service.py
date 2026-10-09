
from smartmoney.models.orderblock import (
    Attempt1Status,
    OrderBlock,
)


class ZoneEntryService:
    def is_first_entry(
        self,
        orderblock: OrderBlock,
        zone_name: str,
        price: float,
        price_low: float,
        price_high: float,
    ) -> bool:
        inside = price_low <= price <= price_high

        if zone_name == "ENTRY":
            is_attempt1 = (
                orderblock.attempt1_status == Attempt1Status.NOT_USED
            )
            was_inside = (
                orderblock.initial_zone_inside
                if is_attempt1
                else orderblock.middle_zone_inside
            )
        elif zone_name == "INITIAL":
            is_attempt1 = True
            was_inside = orderblock.initial_zone_inside
        elif zone_name == "MIDDLE":
            is_attempt1 = False
            was_inside = orderblock.middle_zone_inside
        else:
            raise ValueError(f"Unsupported zone: {zone_name}")

        if inside:
            if was_inside:
                return False

            if is_attempt1:
                orderblock.initial_zone_inside = True
            else:
                orderblock.middle_zone_inside = True

            return True

        if is_attempt1:
            orderblock.initial_zone_inside = False
        else:
            orderblock.middle_zone_inside = False

        return False