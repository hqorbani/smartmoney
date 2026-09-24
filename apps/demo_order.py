import MetaTrader5 as mt5

from smartmoney.trading.mt5_broker_executor import MT5BrokerExecutor
from smartmoney.trading.mt5_client import MT5Client
from smartmoney.trading.trade_plan import TradeDirection, TradePlan


def execute_demo_order(
    executor,
    symbol,
    direction,
    volume,
    stop_loss,
    take_profit,
):
    executor.volume = volume

    trade_direction = (
        TradeDirection.BUY
        if direction.upper() == "BUY"
        else TradeDirection.SELL
    )

    plan = TradePlan(
        symbol=symbol,
        timeframe=1,
        direction=trade_direction,
        entry_price=0.0,
        stop_loss=stop_loss,
        take_profit=take_profit,
        risk_distance=abs(stop_loss - take_profit),
        orderblock_index=0,
    )

    if not executor.initialize():
        raise RuntimeError("MT5 initialize failed")

    try:
        return executor.execute(plan)
    finally:
        executor.shutdown()


def main():
    client = MT5Client()
    executor = MT5BrokerExecutor(
        mt5_client=client,
        volume=0.01,
        use_real_request=True,
    )

    result = execute_demo_order(
        executor=executor,
        symbol="ETHEREUM",
        direction="BUY",
        volume=0.01,
        stop_loss=2625.0,
        take_profit=2656.0,
    )

    print(result)


if __name__ == "__main__":
    main()