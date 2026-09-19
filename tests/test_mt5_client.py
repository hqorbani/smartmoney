import MetaTrader5 as mt5
import pytest

class FakeMT5Module:
    def initialize(self):
        return True

    def shutdown(self):
        return True


def test_mt5_client_initializes_terminal(monkeypatch):
    from smartmoney.trading.mt5_client import MT5Client

    fake = FakeMT5Module()

    monkeypatch.setattr(
        mt5,
        "initialize",
        fake.initialize,
    )

    client = MT5Client()

    assert client.initialize() is True

def test_mt5_client_shuts_down_terminal(monkeypatch):
    from smartmoney.trading.mt5_client import MT5Client

    fake = FakeMT5Module()

    monkeypatch.setattr(
        mt5,
        "shutdown",
        fake.shutdown,
    )

    client = MT5Client()

    assert client.shutdown() is True

def test_mt5_client_sends_order(monkeypatch):
    from smartmoney.trading.mt5_client import MT5Client

    class FakeMT5Module:
        def order_send(self, request):
            return {"retcode": 10009}

    fake = FakeMT5Module()

    monkeypatch.setattr(
        mt5,
        "order_send",
        fake.order_send,
    )

    client = MT5Client()

    request = {
        "symbol": "EURUSD",
        "volume": 1.0,
    }

    assert client.send_order(request) == {
        "retcode": 10009,
    }

def test_mt5_client_checks_order(monkeypatch):
    from smartmoney.trading.mt5_client import MT5Client

    expected = {
        "retcode": 10009,
        "comment": "Done",
    }

    class FakeMT5Module:
        def order_check(self, request):
            return expected

    fake = FakeMT5Module()

    monkeypatch.setattr(
        mt5,
        "order_check",
        fake.order_check,
    )

    client = MT5Client()

    request = {
        "symbol": "EURUSD",
        "volume": 0.01,
    }

    assert client.order_check(request) == expected
    
def test_mt5_client_returns_false_when_initialization_fails(monkeypatch):
    from smartmoney.trading.mt5_client import MT5Client

    class FakeMT5Module:
        def initialize(self):
            return False

    fake = FakeMT5Module()

    monkeypatch.setattr(
        mt5,
        "initialize",
        fake.initialize,
    )

    client = MT5Client()

    assert client.initialize() is False

def test_mt5_client_propagates_order_send_exception(monkeypatch):
    from smartmoney.trading.mt5_client import MT5Client

    def failing_order_send(request):
        raise RuntimeError("MT5 order send failed")

    monkeypatch.setattr(
        mt5,
        "order_send",
        failing_order_send,
    )

    client = MT5Client()

    with pytest.raises(
        RuntimeError,
        match="MT5 order send failed",
    ):
        client.send_order({
            "symbol": "EURUSD",
            "volume": 1.0,
        })

def test_mt5_broker_executor_accepts_mt5_client():
    from smartmoney.trading.mt5_broker_executor import MT5BrokerExecutor

    class FakeMT5Client:
        pass

    client = FakeMT5Client()

    executor = MT5BrokerExecutor(
        client,
    )

    assert executor.mt5_client is client

def test_mt5_client_returns_account_info(monkeypatch):
    from smartmoney.trading.mt5_client import MT5Client

    expected = {
        "login": 123456,
        "balance": 300.0,
    }

    class FakeMT5Module:
        def account_info(self):
            return expected

    fake = FakeMT5Module()

    monkeypatch.setattr(
        mt5,
        "account_info",
        fake.account_info,
    )

    client = MT5Client()

    assert client.account_info() == expected

def test_mt5_client_returns_symbol_info(monkeypatch):
    from smartmoney.trading.mt5_client import MT5Client

    expected = {
        "name": "EURUSD",
        "visible": True,
    }

    def fake_symbol_info(symbol):
        assert symbol == "EURUSD"
        return expected

    monkeypatch.setattr(
        mt5,
        "symbol_info",
        fake_symbol_info,
    )

    client = MT5Client()

    assert client.symbol_info("EURUSD") == expected

def test_mt5_client_returns_symbol_tick(monkeypatch):
    from smartmoney.trading.mt5_client import MT5Client

    expected = {
        "bid": 1.1000,
        "ask": 1.1002,
    }

    def fake_symbol_info_tick(symbol):
        assert symbol == "EURUSD"
        return expected

    monkeypatch.setattr(
        mt5,
        "symbol_info_tick",
        fake_symbol_info_tick,
    )

    client = MT5Client()

    assert client.symbol_info_tick("EURUSD") == expected

def test_mt5_client_selects_symbol(monkeypatch):
    from smartmoney.trading.mt5_client import MT5Client

    def fake_symbol_select(symbol, enable):
        assert symbol == "EURUSD"
        assert enable is True
        return True

    monkeypatch.setattr(
        mt5,
        "symbol_select",
        fake_symbol_select,
    )

    client = MT5Client()

    assert client.symbol_select("EURUSD", True) is True

def test_mt5_client_returns_symbol_volume_constraints(monkeypatch):
    from smartmoney.trading.mt5_client import MT5Client

    expected = {
        "volume_min": 0.01,
        "volume_max": 100.0,
        "volume_step": 0.01,
    }

    def fake_symbol_info(symbol):
        assert symbol == "EURUSD"
        return expected

    monkeypatch.setattr(
        mt5,
        "symbol_info",
        fake_symbol_info,
    )

    client = MT5Client()

    info = client.symbol_info("EURUSD")

    assert info["volume_min"] == 0.01
    assert info["volume_max"] == 100.0
    assert info["volume_step"] == 0.01

def test_market_price_falls_back_to_symbol_info(monkeypatch):
    from smartmoney.trading import mt5_client
    class FakeTick:
        bid = 0.0
        ask = 0.0

    class FakeInfo:
        bid = 1.15409
        ask = 1.15411
        select = True

    monkeypatch.setattr(
        mt5_client.mt5,
        "symbol_info_tick",
        lambda symbol: FakeTick(),
    )

    monkeypatch.setattr(
        mt5_client.mt5,
        "symbol_info",
        lambda symbol: FakeInfo(),
    )

    client = mt5_client.MT5Client()

    price = client.market_price("EURUSD")

    assert price == {
        "bid": 1.15409,
        "ask": 1.15411,
    }

def test_market_price_selects_symbol_when_not_selected(monkeypatch):
    from smartmoney.trading import mt5_client

    class FakeInfo:
        bid = 1.15409
        ask = 1.15411
        select = False

    monkeypatch.setattr(
        mt5_client.mt5,
        "symbol_info",
        lambda symbol: FakeInfo(),
    )

    selected = []

    monkeypatch.setattr(
        mt5_client.mt5,
        "symbol_select",
        lambda symbol, enable: selected.append(
            (symbol, enable)
        ) or True,
    )

    client = mt5_client.MT5Client()

    price = client.market_price("EURUSD")

    assert selected == [("EURUSD", True)]
    assert price == {
        "bid": 1.15409,
        "ask": 1.15411,
    }                                                   