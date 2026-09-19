import MetaTrader5 as mt5

from smartmoney.trading.mt5_broker_executor import MT5BrokerExecutor
from smartmoney.trading.mt5_client import MT5Client
from smartmoney.trading.trade_plan import TradeDirection, TradePlan


def main():
    client = MT5Client()
    executor = MT5BrokerExecutor(
        mt5_client=client,
        volume=0.01,
        use_real_request=True,
    )

    plan = TradePlan(
        symbol="ETHEREUM",
        timeframe=1,
        direction=TradeDirection.BUY,
        entry_price=0.0,
        stop_loss=2625.0,
        take_profit=2656.0,
        risk_distance=10.0,
        orderblock_index=0,
    )

    if not executor.initialize():
        raise RuntimeError("MT5 initialize failed")

    try:
        result = executor.execute(plan)
        print(result)
    finally:
        executor.shutdown()


if __name__ == "__main__":
    main()  