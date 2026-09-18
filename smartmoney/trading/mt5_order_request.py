from smartmoney.trading.trade_plan import (
    TradeDirection,
    TradePlan,
)
import MetaTrader5 as mt5

def build_mt5_order_request(
    plan: TradePlan,
    volume: float,
) -> dict:
    if not plan.symbol:
        raise ValueError(
            "Symbol must not be empty"
        )
    if plan.timeframe <= 0:
        raise ValueError(
            "Timeframe must be positive"
        )
    if plan.risk_distance <= 0:
        raise ValueError(
            "Trade plan risk must be positive"
        )    
    if volume <= 0:
        raise ValueError(
            "Volume must be positive"
        )

    if not isinstance(plan.direction, TradeDirection):
        raise ValueError(
            "Invalid trade direction"
        )
    if plan.direction == TradeDirection.BUY:
        if not (
            plan.stop_loss < plan.entry_price < plan.take_profit
        ):
            raise ValueError(
                "Invalid BUY trade levels"
            )

    elif plan.direction == TradeDirection.SELL:
        if not (
            plan.take_profit < plan.entry_price < plan.stop_loss
        ):
            raise ValueError(
                "Invalid SELL trade levels"
            )
    return {
        "symbol": plan.symbol,
        "volume": volume,
        "direction": plan.direction.value,
        "entry_price": plan.entry_price,
        "stop_loss": plan.stop_loss,
        "take_profit": plan.take_profit,
    }

def build_real_mt5_order_request(
    plan: TradePlan,
    volume: float,
    price: float,
    deviation: int = 20,
    magic: int = 234000,
    comment: str = "smartmoney",
    type_filling: int = 2,
) -> dict:
    if not plan.symbol:
        raise ValueError(
            "Symbol must not be empty"
        )

    if plan.timeframe <= 0:
        raise ValueError(
            "Timeframe must be positive"
        )

    if plan.risk_distance <= 0:
        raise ValueError(
            "Trade plan risk must be positive"
        )

    if volume <= 0:
        raise ValueError(
            "Volume must be positive"
        )

    if price <= 0:
        raise ValueError(
            "Price must be positive"
        )

    if not isinstance(plan.direction, TradeDirection):
        raise ValueError(
            "Invalid trade direction"
        )

    if plan.direction == TradeDirection.BUY:
        order_type = mt5.ORDER_TYPE_BUY

        if not (
            plan.stop_loss < price < plan.take_profit
        ):
            raise ValueError(
                "Invalid BUY trade levels"
            )

    else:
        order_type = mt5.ORDER_TYPE_SELL

        if not (
            plan.take_profit < price < plan.stop_loss
        ):
            raise ValueError(
                "Invalid SELL trade levels"
            )

    return {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": plan.symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "sl": plan.stop_loss,
        "tp": plan.take_profit,
        "deviation": deviation,
        "magic": magic,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": type_filling,
    }