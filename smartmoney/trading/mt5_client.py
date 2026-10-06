import MetaTrader5 as mt5
from smartmoney.models.symbol_trading_info import SymbolTradingInfo

class MT5Client:
    """
    Thin adapter around the MetaTrader5 Python module.
    """

    def initialize(self) -> bool:
        return mt5.initialize()

    def shutdown(self) -> bool:
        return mt5.shutdown()

    def send_order(self, request: dict):
        return mt5.order_send(request)

    def order_check(self, request):
        return mt5.order_check(request)

    def account_info(self):
        return mt5.account_info()

    def positions_get(self, symbol: str | None = None):
        return mt5.positions_get(symbol=symbol)

    def symbol_info(self, symbol: str):
        return mt5.symbol_info(symbol)

    def symbol_info_tick(self, symbol: str):
        return mt5.symbol_info_tick(symbol)

    def symbol_select(
        self,
        symbol: str,
        enable: bool,
    ) -> bool:
        return mt5.symbol_select(
            symbol,
            enable,
        )

    def market_price(self, symbol: str) -> dict:
        info = self.symbol_info(symbol)

        if info is None:
            raise ValueError(
                f"Symbol not found: {symbol}"
            )

        if not info.select:
            if not self.symbol_select(symbol, True):
                raise ValueError(
                    f"Failed to select symbol: {symbol}"
                )

            info = self.symbol_info(symbol)

            if info is None:
                raise ValueError(
                    f"Symbol not found after selection: {symbol}"
                )

        tick = self.symbol_info_tick(symbol)

        if (
            tick is not None
            and tick.bid > 0
            and tick.ask > 0
        ):
            return {
                "bid": tick.bid,
                "ask": tick.ask,
            }

        if (
            info.bid > 0
            and info.ask > 0
        ):
            return {
                "bid": info.bid,
                "ask": info.ask,
            }

        raise ValueError(
            f"No valid market price for {symbol}"
        )

    def get_symbol_trading_info(
        self,
        symbol: str,
    ) -> SymbolTradingInfo:
        info = self.symbol_info(symbol)

        if info is None:
            raise ValueError(f"Symbol not found: {symbol}")

        return SymbolTradingInfo(
            tick_size=float(info.trade_tick_size),
            tick_value=float(info.trade_tick_value),
            contract_size=float(info.trade_contract_size),
            digits=int(info.digits),
            volume_min=float(info.volume_min),
            volume_max=float(info.volume_max),
            volume_step=float(info.volume_step),
        )