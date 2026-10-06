from smartmoney.models.symbol_trading_info import SymbolTradingInfo


def test_symbol_trading_info_stores_broker_metadata():
    info = SymbolTradingInfo(
        tick_size=0.00001,
        tick_value=1.0,
        contract_size=100_000.0,
        digits=5,
        volume_min=0.01,
        volume_max=100.0,
        volume_step=0.01,
    )

    assert info.tick_size == 0.00001
    assert info.tick_value == 1.0
    assert info.contract_size == 100_000.0
    assert info.digits == 5
    assert info.volume_min == 0.01
    assert info.volume_max == 100.0
    assert info.volume_step == 0.01