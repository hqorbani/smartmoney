from smartmoney.trading.mt5_client import MT5Client


def test_real_mt5_client_initializes_and_shuts_down():
    client = MT5Client()

    assert client.initialize() is True
    assert client.shutdown() is True

from smartmoney.trading.mt5_client import MT5Client


def test_real_mt5_client_returns_eurusd_symbol_info():
    client = MT5Client()

    assert client.initialize() is True

    try:
        info = client.symbol_info("EURUSD")

        assert info is not None
        assert info.volume_min > 0
        assert info.volume_max >= info.volume_min
        assert info.volume_step > 0
    finally:
        client.shutdown()

def test_real_mt5_client_returns_eurusd_tick():
    client = MT5Client()

    assert client.initialize() is True

    try:
        tick = client.symbol_info_tick("EURUSD")

        assert tick is not None
        assert tick.bid > 0
        assert tick.ask > 0
        assert tick.ask >= tick.bid
    finally:
        client.shutdown()

def test_real_mt5_client_returns_eurusd_market_price():
    client = MT5Client()

    assert client.initialize() is True

    try:
        info = client.symbol_info("EURUSD")

        assert info is not None
        assert info.bid > 0
        assert info.ask > 0
        assert info.ask >= info.bid
    finally:
        client.shutdown()

def test_real_mt5_client_returns_valid_eurusd_market_price():
    client = MT5Client()

    assert client.initialize() is True

    try:
        price = client.market_price("EURUSD")

        assert price["bid"] > 0
        assert price["ask"] > 0
        assert price["ask"] >= price["bid"]
    finally:
        client.shutdown()

def test_real_mt5_client_returns_eurusd_volume_constraints():
    client = MT5Client()

    assert client.initialize() is True

    try:
        info = client.symbol_info("EURUSD")

        assert info is not None
        assert info.volume_min > 0
        assert info.volume_max >= info.volume_min
        assert info.volume_step > 0
        assert (
            info.volume_min
            <= info.volume_step * round(
                info.volume_min / info.volume_step
            )
            <= info.volume_max
        )
    finally:
        client.shutdown()                                   