import MetaTrader5 as mt5
import pandas as pd


class MT5DataProvider:
    """Wrapper around MetaTrader5 package."""

    def __init__(self) -> None:
        self._connected = False

    def connect(self) -> None:
        """Initialize connection to MetaTrader5."""

        if self._connected:
            return

        if not mt5.initialize():
            code, message = mt5.last_error()
            raise RuntimeError(
                f"MT5 initialize failed ({code}): {message}"
            )

        self._connected = True

    def shutdown(self) -> None:
        """Shutdown MetaTrader5 connection."""

        if self._connected:
            mt5.shutdown()
            self._connected = False

    def is_connected(self) -> bool:
        """Return current connection status."""

        return self._connected

    def get_account_balance(self) -> float:
        """Return current account balance."""
        account = mt5.account_info()

        if account is None:
            code, message = mt5.last_error()
            raise RuntimeError(
                f"Cannot get account information ({code}): {message}"
            )

        return float(account.balance)

    def symbol_select(self, symbol: str) -> None:
        """Ensure symbol is available in Market Watch."""

        if not mt5.symbol_select(symbol, True):
            code, message = mt5.last_error()
            raise RuntimeError(
                f"Cannot select symbol '{symbol}' ({code}): {message}"
            )

    def symbol_info(self, symbol: str):
        """Return symbol information."""

        return mt5.symbol_info(symbol)

    def fetch_rates(
        self,
        symbol: str,
        timeframe: int,
        count: int,
    ) -> pd.DataFrame:
        """
        Fetch latest candles.

        Returns
        -------
        DataFrame
            Columns:
            time, open, high, low, close,
            tick_volume, spread, real_volume
        """

        self.symbol_select(symbol)

        rates = mt5.copy_rates_from_pos(
            symbol,
            timeframe,
            0,
            count,
        )

        if rates is None:
            code, message = mt5.last_error()
            raise RuntimeError(
                f"Cannot fetch rates ({code}): {message}"
            )

        return self._prepare_dataframe(rates)

    def fetch_last_closed(
        self,
        symbol: str,
        timeframe: int,
    ) -> pd.DataFrame:
        """
        Fetch the latest closed candle.
        """

        self.symbol_select(symbol)

        rates = mt5.copy_rates_from_pos(
            symbol,
            timeframe,
            1,
            1,
        )

        if rates is None:
            code, message = mt5.last_error()
            raise RuntimeError(
                f"Cannot fetch last candle ({code}): {message}"
            )

        return self._prepare_dataframe(rates)

    @staticmethod
    def _prepare_dataframe(rates) -> pd.DataFrame:
        """Convert MT5 output into a clean DataFrame."""

        df = pd.DataFrame(rates)

        df["time"] = pd.to_datetime(
            df["time"],
            unit="s",
        )

        return df
    
    def get_current_tick(
        self,
        symbol: str,
    ):
        """
        Return current market tick.
        """

        self.symbol_select(symbol)

        tick = mt5.symbol_info_tick(symbol)

        if tick is None:

            code, message = mt5.last_error()

            raise RuntimeError(
                f"Cannot get current tick ({code}): {message}"
            )

        return tick
    
    def get_current_price(
        self,
        symbol: str,
    ) -> float:
        """
        Return current market price.

        Mid price is used:
            (Bid + Ask) / 2
        """

        tick = self.get_current_tick(symbol)

        return (tick.bid + tick.ask) / 2