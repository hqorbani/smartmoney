from smartmoney.models.orderblock import OrderBlock


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

        if zone_name == "INITIAL":
            was_inside = orderblock.initial_zone_inside
        elif zone_name == "MIDDLE":
            was_inside = orderblock.middle_zone_inside
        else:
            raise ValueError(f"Unsupported zone: {zone_name}")

        if not inside:
            if zone_name == "INITIAL":
                orderblock.initial_zone_inside = False
            else:
                orderblock.middle_zone_inside = False
            return False

        if was_inside:
            return False

        if zone_name == "INITIAL":
            orderblock.initial_zone_inside = True
        else:
            orderblock.middle_zone_inside = True

        return True