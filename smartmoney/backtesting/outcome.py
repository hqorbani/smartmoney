from dataclasses import dataclass
from enum import Enum

import pandas as pd

from smartmoney.models.orderblock import OrderBlock


class TradeOutcome(Enum):
    WIN = "win"
    LOSS = "loss"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True, slots=True)
class TradeOutcomeResult:
    entry_price: float
    stop_loss: float
    take_profit: float
    risk: float
    reward: float
    outcome: TradeOutcome
    exit_index: int | None
    exit_price: float | None
    mfe: float
    mae: float


def calculate_entry_price(
    ob: OrderBlock,
    candle_low: float,
    candle_high: float,
) -> float:
    """
    Calculate the actual executable entry price from the first-touch candle.

    Bullish OBs are approached from above, so the candle low is the
    first-touch price inside the OB.

    Bearish OBs are approached from below, so the candle high is the
    first-touch price inside the OB.
    """
    if ob.high <= ob.low:
        raise ValueError("Order Block high must be greater than low")

    if candle_low > ob.high or candle_high < ob.low:
        raise ValueError("Candle does not touch the Order Block")

    if ob.bullish:
        return min(ob.high, max(ob.low, float(candle_low)))

    return min(ob.high, max(ob.low, float(candle_high)))


def calculate_trade_levels(
    ob: OrderBlock,
    entry_price: float,
    rr: float,
) -> tuple[float, float, float]:
    """
    Return (stop_loss, take_profit, risk).
    """
    if rr <= 0:
        raise ValueError("Risk-reward ratio must be positive")

    if not ob.low <= entry_price <= ob.high:
        raise ValueError("Entry price must be inside the Order Block")

    if ob.bullish:
        stop_loss = ob.low
        risk = entry_price - stop_loss
        take_profit = entry_price + risk * rr
    else:
        stop_loss = ob.high
        risk = stop_loss - entry_price
        take_profit = entry_price - risk * rr

    if risk <= 0:
        raise ValueError("Entry price must leave positive risk")

    return stop_loss, take_profit, risk


def simulate_outcome(
    df: pd.DataFrame,
    ob: OrderBlock,
    touch_index: int,
    entry_price: float,
    rr: float,
) -> TradeOutcomeResult:
    """
    Simulate the trade after the first-touch candle.

    The touch candle itself is excluded because OHLC data does not tell us
    whether TP or SL was reached first inside that candle.

    If both TP and SL are touched in the same future candle, the result is
    conservatively classified as LOSS.
    """
    required_columns = {"high", "low"}

    missing = required_columns.difference(df.columns)

    if missing:
        raise ValueError(
            f"DataFrame is missing required columns: {sorted(missing)}"
        )

    if touch_index < 0 or touch_index >= len(df):
        raise ValueError("touch_index is outside the DataFrame")

    stop_loss, take_profit, risk = calculate_trade_levels(
        ob=ob,
        entry_price=entry_price,
        rr=rr,
    )

    mfe = 0.0
    mae = 0.0

    for index in range(touch_index + 1, len(df)):
        candle = df.iloc[index]
        candle_high = float(candle["high"])
        candle_low = float(candle["low"])

        if ob.bullish:
            mfe = max(mfe, candle_high - entry_price)
            mae = max(mae, entry_price - candle_low)

            hit_stop = candle_low <= stop_loss
            hit_target = candle_high >= take_profit
        else:
            mfe = max(mfe, entry_price - candle_low)
            mae = max(mae, candle_high - entry_price)

            hit_stop = candle_high >= stop_loss
            hit_target = candle_low <= take_profit

        if hit_stop and hit_target:
            return TradeOutcomeResult(
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk=risk,
                reward=risk * rr,
                outcome=TradeOutcome.LOSS,
                exit_index=index,
                exit_price=stop_loss,
                mfe=mfe,
                mae=mae,
            )

        if hit_stop:
            return TradeOutcomeResult(
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk=risk,
                reward=risk * rr,
                outcome=TradeOutcome.LOSS,
                exit_index=index,
                exit_price=stop_loss,
                mfe=mfe,
                mae=mae,
            )

        if hit_target:
            return TradeOutcomeResult(
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk=risk,
                reward=risk * rr,
                outcome=TradeOutcome.WIN,
                exit_index=index,
                exit_price=take_profit,
                mfe=mfe,
                mae=mae,
            )

    return TradeOutcomeResult(
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        risk=risk,
        reward=risk * rr,
        outcome=TradeOutcome.UNRESOLVED,
        exit_index=None,
        exit_price=None,
        mfe=mfe,
        mae=mae,
    )