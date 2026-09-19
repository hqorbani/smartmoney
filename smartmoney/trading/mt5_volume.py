def calculate_mt5_volume(
    risk_amount: float,
    stop_distance: float,
    trade_tick_value: float,
    trade_tick_size: float,
    volume_step: float,
    volume_min: float | None = None,
    volume_max: float | None = None,
) -> float:
    if risk_amount <= 0:
        raise ValueError("Risk amount must be positive")

    if stop_distance <= 0:
        raise ValueError("Stop distance must be positive")

    if trade_tick_size <= 0:
        raise ValueError("Trade tick size must be positive")

    if trade_tick_value <= 0:
        raise ValueError("Trade tick value must be positive")

    if volume_step <= 0:
        raise ValueError("Volume step must be positive")
    loss_per_volume = (
        stop_distance / trade_tick_size
    ) * trade_tick_value

    raw_volume = risk_amount / loss_per_volume

    volume = (
        int(raw_volume / volume_step)
        * volume_step
    )

    if volume_min is not None and volume < volume_min:
        raise ValueError("Calculated volume is below minimum")

    if volume_max is not None and volume > volume_max:
        raise ValueError("Calculated volume is above maximum")

    return volume
