from dataclasses import dataclass
from enum import Enum

import pandas as pd

from smartmoney.models.orderblock import OrderBlock


class OrderBlockDepthZone(Enum):
    FIRST = "first"
    MIDDLE = "middle"
    FINAL = "final"


@dataclass(frozen=True, slots=True)
class OrderBlockTouch:
    index: int
    zone: OrderBlockDepthZone
    penetration: float


def _validate_orderblock(ob: OrderBlock) -> None:
    if ob.high <= ob.low:
        raise ValueError("Order Block high must be greater than low")


def _validate_dataframe(df: pd.DataFrame) -> None:
    required_columns = {"high", "low"}
    missing = required_columns.difference(df.columns)

    if missing:
        raise ValueError(
            f"DataFrame is missing required columns: {sorted(missing)}"
        )


def zone_boundaries(
    ob: OrderBlock,
) -> dict[OrderBlockDepthZone, tuple[float, float]]:
    """
    Return the three equal-depth zones of an Order Block.

    Each tuple is (lower_price, upper_price).

    For bullish OBs, price is expected to approach from above,
    so FIRST is the upper third and FINAL is the deepest third.

    For bearish OBs, price is expected to approach from below,
    so FIRST is the lower third and FINAL is the deepest third.
    """
    _validate_orderblock(ob)

    depth = ob.high - ob.low
    third = depth / 3.0

    if ob.bullish:
        return {
            OrderBlockDepthZone.FIRST: (
                ob.high - third,
                ob.high,
            ),
            OrderBlockDepthZone.MIDDLE: (
                ob.high - 2.0 * third,
                ob.high - third,
            ),
            OrderBlockDepthZone.FINAL: (
                ob.low,
                ob.high - 2.0 * third,
            ),
        }

    return {
        OrderBlockDepthZone.FIRST: (
            ob.low,
            ob.low + third,
        ),
        OrderBlockDepthZone.MIDDLE: (
            ob.low + third,
            ob.low + 2.0 * third,
        ),
        OrderBlockDepthZone.FINAL: (
            ob.low + 2.0 * third,
            ob.high,
        ),
    }


def _penetration(
    ob: OrderBlock,
    candle_low: float,
    candle_high: float,
) -> float | None:
    """
    Return the deepest penetration into the OB as a fraction [0, 1].

    None means the candle does not overlap the Order Block.
    """
    if candle_low > ob.high or candle_high < ob.low:
        return None

    depth = ob.high - ob.low

    if ob.bullish:
        penetration = (ob.high - candle_low) / depth
    else:
        penetration = (candle_high - ob.low) / depth

    return min(1.0, max(0.0, penetration))


def _zone_from_penetration(
    penetration: float,
) -> OrderBlockDepthZone:
    one_third = 1.0 / 3.0
    two_thirds = 2.0 / 3.0

    if penetration <= one_third:
        return OrderBlockDepthZone.FIRST

    if penetration <= two_thirds:
        return OrderBlockDepthZone.MIDDLE

    return OrderBlockDepthZone.FINAL


def find_first_touch(
    df: pd.DataFrame,
    ob: OrderBlock,
    start_index: int | None = None,
) -> OrderBlockTouch | None:
    """
    Find the first candle that overlaps the Order Block.

    The search is strictly forward from start_index.

    If start_index is omitted, the Order Block's related FVG must exist
    and the search starts at the candle immediately after FVG confirmation.

    The OrderBlock itself is never mutated.
    """
    _validate_orderblock(ob)
    _validate_dataframe(df)

    if start_index is None:
        if ob.related_fvg is None:
            raise ValueError(
                "start_index is required when Order Block has no related FVG"
            )

        start_index = ob.related_fvg.end_index + 1

    if start_index < 0:
        raise ValueError("start_index must be non-negative")

    for index in range(start_index, len(df)):
        candle = df.iloc[index]

        penetration = _penetration(
            ob,
            candle_low=float(candle["low"]),
            candle_high=float(candle["high"]),
        )

        if penetration is None:
            continue

        return OrderBlockTouch(
            index=index,
            zone=_zone_from_penetration(penetration),
            penetration=penetration,
        )

    return None