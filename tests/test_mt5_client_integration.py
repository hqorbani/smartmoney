from smartmoney.trading.mt5_client import MT5Client
import MetaTrader5 as mt5

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

def test_real_mt5_client_order_check_eurusd():
    client = MT5Client()

    assert client.initialize() is True

    try:
        info = client.symbol_info("EURUSD")
        tick = client.symbol_info_tick("EURUSD")

        assert info is not None
        assert tick is not None

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": "EURUSD",
            "volume": info.volume_min,
            "type": mt5.ORDER_TYPE_BUY,
            "price": tick.ask,
            "sl": tick.ask - 0.0010,
            "tp": tick.ask + 0.0020,
            "deviation": 20,
            "magic": 123456,
            "comment": "smartmoney order check",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": 0,
        }

        result = client.order_check(request)

        print(result)

        assert result is not None
        assert result.retcode == 0

    finally:
        client.shutdown()        