def test_mt5_volume_is_calculated_from_risk_and_symbol_ticks():
    from smartmoney.trading.mt5_volume import calculate_mt5_volume

    volume = calculate_mt5_volume(
        risk_amount=1.0,
        stop_distance=10.0,
        trade_tick_value=0.05,
        trade_tick_size=0.01,
        volume_step=0.01,
    )

    assert volume == 0.02


def test_mt5_volume_rejects_volume_below_minimum():
    from smartmoney.trading.mt5_volume import calculate_mt5_volume

    try:
        calculate_mt5_volume(
            risk_amount=0.4,
            stop_distance=10.0,
            trade_tick_value=0.05,
            trade_tick_size=0.01,
            volume_step=0.01,
            volume_min=0.01,
        )
    except ValueError as exc:
        assert str(exc) == "Calculated volume is below minimum"
    else:
        raise AssertionError("Expected ValueError")

def test_mt5_volume_rounds_down_to_volume_step():
    from smartmoney.trading.mt5_volume import calculate_mt5_volume

    volume = calculate_mt5_volume(
        risk_amount=1.25,
        stop_distance=10.0,
        trade_tick_value=0.05,
        trade_tick_size=0.01,
        volume_step=0.01,
    )

    assert volume == 0.02

def test_mt5_volume_rejects_volume_above_maximum():
    from smartmoney.trading.mt5_volume import calculate_mt5_volume

    try:
        calculate_mt5_volume(
            risk_amount=1000.0,
            stop_distance=10.0,
            trade_tick_value=0.05,
            trade_tick_size=0.01,
            volume_step=0.01,
            volume_max=1.0,
        )
    except ValueError as exc:
        assert str(exc) == "Calculated volume is above maximum"
    else:
        raise AssertionError("Expected ValueError")

def test_mt5_volume_rejects_non_positive_inputs():
    from smartmoney.trading.mt5_volume import calculate_mt5_volume

    try:
        calculate_mt5_volume(
            risk_amount=0.0,
            stop_distance=10.0,
            trade_tick_value=0.05,
            trade_tick_size=0.01,
            volume_step=0.01,
        )
    except ValueError as exc:
        assert str(exc) == "Risk amount must be positive"
    else:
        raise AssertionError("Expected ValueError")

def test_mt5_volume_rejects_non_positive_stop_distance():
    from smartmoney.trading.mt5_volume import calculate_mt5_volume

    try:
        calculate_mt5_volume(
            risk_amount=1.0,
            stop_distance=0.0,
            trade_tick_value=0.05,
            trade_tick_size=0.01,
            volume_step=0.01,
        )
    except ValueError as exc:
        assert str(exc) == "Stop distance must be positive"
    else:
        raise AssertionError("Expected ValueError")

def test_mt5_volume_rejects_non_positive_tick_size():
    from smartmoney.trading.mt5_volume import calculate_mt5_volume

    try:
        calculate_mt5_volume(
            risk_amount=1.0,
            stop_distance=10.0,
            trade_tick_value=0.05,
            trade_tick_size=0.0,
            volume_step=0.01,
        )
    except ValueError as exc:
        assert str(exc) == "Trade tick size must be positive"
    else:
        raise AssertionError("Expected ValueError")

def test_mt5_volume_rejects_non_positive_tick_value():
    from smartmoney.trading.mt5_volume import calculate_mt5_volume

    try:
        calculate_mt5_volume(
            risk_amount=1.0,
            stop_distance=10.0,
            trade_tick_value=0.0,
            trade_tick_size=0.01,
            volume_step=0.01,
        )
    except ValueError as exc:
        assert str(exc) == "Trade tick value must be positive"
    else:
        raise AssertionError("Expected ValueError")

def test_mt5_volume_rejects_non_positive_volume_step():
    from smartmoney.trading.mt5_volume import calculate_mt5_volume

    try:
        calculate_mt5_volume(
            risk_amount=1.0,
            stop_distance=10.0,
            trade_tick_value=0.05,
            trade_tick_size=0.01,
            volume_step=0.0,
        )
    except ValueError as exc:
        assert str(exc) == "Volume step must be positive"
    else:
        raise AssertionError("Expected ValueError")
