from pathlib import Path

import pandas as pd

from smartmoney.backtesting.research import HistoricalResearchResult


def _get_exit_time(
    df: pd.DataFrame,
    exit_index: int | None,
) -> pd.Timestamp | None:
    if exit_index is None:
        return None

    if exit_index < 0 or exit_index >= len(df):
        raise ValueError(
            f"exit_index {exit_index} is outside the DataFrame"
        )

    return df.iloc[exit_index]["time"]


def export_backtest_trade_details_to_excel(
    result: HistoricalResearchResult,
    output_path: Path,
) -> None:
    """
    Export detailed backtest trade information to an Excel file.
    """
    rows: list[dict[str, object]] = []

    for trade in result.trades:
        touch_candle = result.df.iloc[trade.touch_index]

        outcome_1r = trade.outcome_1r
        outcome_2r = trade.outcome_2r

        row: dict[str, object] = {
            # ==================================================
            # Research
            # ==================================================
            "symbol": result.symbol,
            "timeframe": result.timeframe,

            # ==================================================
            # Order Block
            # ==================================================
            "ob_index": trade.orderblock.index,
            "ob_time": trade.orderblock.time,
            "ob_direction": (
                "bullish"
                if trade.orderblock.bullish
                else "bearish"
            ),
            "ob_open": trade.orderblock.open,
            "ob_high": trade.orderblock.high,
            "ob_low": trade.orderblock.low,
            "ob_close": trade.orderblock.close,

            # ==================================================
            # First Touch
            # ==================================================
            "touch_index": trade.touch_index,
            "touch_time": touch_candle["time"],
            "touch_zone": trade.touch_zone.value,
            "penetration": trade.penetration,
            "max_ob_penetration": trade.max_ob_penetration,

            # ==================================================
            # Entry
            # ==================================================
            "entry_price": trade.entry_price,

            # ==================================================
            # 1R
            # ==================================================
            "stop_loss_1r": (
                outcome_1r.stop_loss
                if outcome_1r is not None
                else None
            ),
            "take_profit_1r": (
                outcome_1r.take_profit
                if outcome_1r is not None
                else None
            ),
            "risk_1r": (
                outcome_1r.risk
                if outcome_1r is not None
                else None
            ),
            "reward_1r": (
                outcome_1r.reward
                if outcome_1r is not None
                else None
            ),
            "outcome_1r": (
                outcome_1r.outcome.value
                if outcome_1r is not None
                else "ZERO_RISK"
            ),
            "exit_index_1r": (
                outcome_1r.exit_index
                if outcome_1r is not None
                else None
            ),
            "exit_time_1r": (
                _get_exit_time(
                    result.df,
                    outcome_1r.exit_index,
                )
                if outcome_1r is not None
                else None
            ),
            "exit_price_1r": (
                outcome_1r.exit_price
                if outcome_1r is not None
                else None
            ),
            "mfe_1r": (
                outcome_1r.mfe
                if outcome_1r is not None
                else None
            ),
            "mae_1r": (
                outcome_1r.mae
                if outcome_1r is not None
                else None
            ),

            # ==================================================
            # 2R
            # ==================================================
            "stop_loss_2r": (
                outcome_2r.stop_loss
                if outcome_2r is not None
                else None
            ),
            "take_profit_2r": (
                outcome_2r.take_profit
                if outcome_2r is not None
                else None
            ),
            "risk_2r": (
                outcome_2r.risk
                if outcome_2r is not None
                else None
            ),
            "reward_2r": (
                outcome_2r.reward
                if outcome_2r is not None
                else None
            ),
            "outcome_2r": (
                outcome_2r.outcome.value
                if outcome_2r is not None
                else "ZERO_RISK"
            ),
            "exit_index_2r": (
                outcome_2r.exit_index
                if outcome_2r is not None
                else None
            ),
            "exit_time_2r": (
                _get_exit_time(
                    result.df,
                    outcome_2r.exit_index,
                )
                if outcome_2r is not None
                else None
            ),
            "exit_price_2r": (
                outcome_2r.exit_price
                if outcome_2r is not None
                else None
            ),
            "mfe_2r": (
                outcome_2r.mfe
                if outcome_2r is not None
                else None
            ),
            "mae_2r": (
                outcome_2r.mae
                if outcome_2r is not None
                else None
            ),
        }

        rows.append(row)

    export_df = pd.DataFrame(rows)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    export_df.to_excel(
        output_path,
        index=False,
    )