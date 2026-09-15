from smartmoney.backtesting.outcome import calculate_trade_levels
from smartmoney.models.orderblock import OrderBlock
from smartmoney.trading.trade_plan import TradeDirection, TradePlan


class TradePlanner:
    """
    Build a trade plan from a confirmed Order Block.

    This class only creates trade plans.
    It does not send orders or interact with MT5.
    """

    def __init__(
        self,
        symbol: str,
        timeframe: int,
        rr: float,
    ) -> None:
        if not symbol:
            raise ValueError("Symbol must not be empty")

        if rr <= 0:
            raise ValueError("Risk-reward ratio must be positive")

        self.symbol = symbol
        self.timeframe = timeframe
        self.rr = rr

    def create_plan(
        self,
        ob: OrderBlock,
        entry_price: float,
    ) -> TradePlan:
        stop_loss, take_profit, risk = calculate_trade_levels(
            ob=ob,
            entry_price=entry_price,
            rr=self.rr,
        )

        direction = (
            TradeDirection.BUY
            if ob.bullish
            else TradeDirection.SELL
        )

        return TradePlan(
            symbol=self.symbol,
            timeframe=self.timeframe,
            direction=direction,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_distance=risk,
            orderblock_index=ob.index,
        )