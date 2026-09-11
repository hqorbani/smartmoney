from pathlib import Path

import pandas as pd

from smartmoney.backtesting.orderblock_zones import OrderBlockDepthZone
from smartmoney.backtesting.outcome import (
    TradeOutcome,
    TradeOutcomeResult,
)
from smartmoney.backtesting.research import HistoricalResearchResult
from smartmoney.backtesting.runner import BacktestTrade
from smartmoney.backtesting.trade_export import (
    export_backtest_trade_details_to_excel,
)
from smartmoney.models.orderblock import OrderBlock


def test_export_backtest_trade_details_to_excel(
    tmp_path: Path,
):
    df = pd.DataFrame(
        {
            "time": pd.to_datetime(
                [
                    "2026-01-01 00:00:00",
                    "2026-01-01 00:01:00",
                    "2026-01-01 00:02:00",
                    "2026-01-01 00:03:00",
                ]
            ),
            "open": [100.0, 101.0, 102.0, 103.0],
            "high": [101.0, 102.0, 103.0, 104.0],
            "low": [99.0, 100.0, 101.0, 102.0],
            "close": [100.5, 101.5, 102.5, 103.5],
        }
    )

    ob = OrderBlock(
        index=0,
        time=df.iloc[0]["time"],
        open=100.0,
        high=101.0,
        low=99.0,
        close=100.5,
        bullish=True,
    )

    outcome_1r = TradeOutcomeResult(
        entry_price=100.0,
        stop_loss=99.0,
        take_profit=101.0,
        risk=1.0,
        reward=1.0,
        outcome=TradeOutcome.WIN,
        exit_index=3,
        exit_price=101.0,
        mfe=1.0,
        mae=0.5,
    )

    trade = BacktestTrade(
        orderblock=ob,
        touch_index=1,
        touch_zone=OrderBlockDepthZone.FIRST,
        penetration=0.2,
        max_ob_penetration=0.8,
        entry_price=100.0,
        outcome_1r=outcome_1r,
        outcome_2r=None,
    )

    result = HistoricalResearchResult(
        symbol="NAS100",
        timeframe=1,
        candle_count=len(df),
        df=df,
        trades=[trade],
        zone_stats={},
    )

    output_path = tmp_path / "trades.xlsx"

    export_backtest_trade_details_to_excel(
        result=result,
        output_path=output_path,
    )

    assert output_path.exists()

    exported = pd.read_excel(output_path)

    assert len(exported) == 1

    row = exported.iloc[0]

    assert row["symbol"] == "NAS100"
    assert row["timeframe"] == 1

    assert row["touch_index"] == 1
    assert row["touch_zone"] == "first"

    assert row["entry_price"] == 100.0

    assert row["stop_loss_1r"] == 99.0
    assert row["take_profit_1r"] == 101.0
    assert row["outcome_1r"] == TradeOutcome.WIN.value
    assert row["exit_index_1r"] == 3
    assert row["exit_price_1r"] == 101.0

    assert row["outcome_2r"] == "ZERO_RISK"