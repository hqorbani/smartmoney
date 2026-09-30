import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import MetaTrader5 as mt5
import pandas as pd

from smartmoney.bootstrap import create_provider, create_signal_scanner
from smartmoney.config import Config
from smartmoney.models.fvg import FVGStatus

SYMBOL = "XAUUSD"
TIMEFRAME = 3

TARGET_TIME = datetime(2026, 9, 28, 16, 48)

HISTORY = Config.HISTORY_BARS


def get_historical_dataframe(snapshot_time=TARGET_TIME):
    """
    Build the same rolling history used by the live scanner:

    - fetch enough recent M3 candles
    - keep only candles strictly before snapshot_time
    - keep exactly the last HISTORY closed candles
    """

    rates = mt5.copy_rates_from_pos(
        SYMBOL,
        mt5.TIMEFRAME_M3,
        0,
        HISTORY + 300,
    )

    if rates is None:
        raise RuntimeError(
            f"MT5 copy_rates_from_pos failed: {mt5.last_error()}"
        )

    df = pd.DataFrame(rates)

    if df.empty:
        raise RuntimeError("MT5 returned no candles.")

    df["time"] = pd.to_datetime(df["time"], unit="s")

    df = df.sort_values("time").reset_index(drop=True)

    df = df[df["time"] < snapshot_time].copy()

    if len(df) < HISTORY:
        raise RuntimeError(
            f"Only {len(df)} candles before {snapshot_time}; "
            f"need {HISTORY}."
        )

    return df.iloc[-HISTORY:].copy().reset_index(drop=True)

def main():
    print("Historical persistent-context OB/FVG diagnostic")
    print(f"Symbol      : {SYMBOL}")
    print(f"Timeframe   : M3")
    print(f"Target time : {TARGET_TIME}")
    print(f"History     : {HISTORY}")

    provider = create_provider()

    if not mt5.initialize():
        raise RuntimeError(
            f"MT5 initialize failed: {mt5.last_error()}"
        )

    try:
        # Use the same ContextManager and AnalyzerEngine
        # that the live SignalScanner uses.
        scanner = create_signal_scanner(provider)

        context_manager = scanner.context_manager
        analyzer_engine = scanner.analyzer_engine

        snapshot_times = pd.date_range(
            start="2026-09-28 16:15:00",
            end="2026-09-28 16:48:00",
            freq="3min",
        )

        target_ob_time = pd.Timestamp("2026-09-28 16:09:00")

        print()
        print("=" * 90)
        print("PERSISTENT CONTEXT TRACE")
        print("=" * 90)

        for snapshot_time in snapshot_times:
            df = get_historical_dataframe(snapshot_time)

            context = context_manager.update(
                SYMBOL,
                TIMEFRAME,
                df,
            )
            ob_count_before = len(context.orderblocks)

            analyzer_engine.run(context)
            if snapshot_time == pd.Timestamp("2026-09-28 16:48:00"):
                from smartmoney.scanners.orderblock_active_fvg import (
                    OrderBlockActiveFVGScanner,
                )
                print()
                print("=" * 90)
                print("ACTUAL ORDER BLOCK + ACTIVE FVG SCANNER OUTPUT")
                print("=" * 90)

                ob_fvg_scanner = OrderBlockActiveFVGScanner()
                signals = ob_fvg_scanner.scan(context)

                print(f"SIGNAL_COUNT={len(signals)}")

                for signal in signals:
                    print(
                        f"SIGNAL_ID={signal.signal_id} | "
                        f"direction={signal.direction} | "
                        f"time={signal.time} | "
                        f"OB_ZONE={signal.price_low} -> {signal.price_high}"
                    )
                print()
                print("=" * 90)
                print("ACTIVE OB + ACTIVE FVG SIGNAL CANDIDATES")
                print("=" * 90)

                for ob in context.orderblocks:
                    if ob.related_fvg is None:
                        continue

                    if ob.related_fvg.status != FVGStatus.ACTIVE:
                        continue

                    if ob.mitigated:
                        continue

                    print(
                        f"OB={ob.time} | "
                        f"direction={'BUY' if ob.bullish else 'SELL'} | "
                        f"status={ob.status} | "
                        f"OB_ZONE={ob.expanded_low} -> {ob.expanded_high} | "
                        f"FVG="
                        f"{ob.related_fvg.start_time} -> "
                        f"{ob.related_fvg.end_time} | "
                        f"FVG_STATUS={ob.related_fvg.status}"
                    )
            if len(context.orderblocks) > ob_count_before:
                print("    NEW OBs ADDED:")

                for ob in context.orderblocks[ob_count_before:]:
                    fvg = ob.related_fvg

                    print(
                        "        "
                        f"OB={ob.time} | "
                        f"direction={'BUY' if ob.bullish else 'SELL'} | "
                        f"mitigated={ob.mitigated} | "
                        f"status={ob.status} | "
                        f"FVG="
                        f"{fvg.start_time if fvg else None}"
                        f" -> "
                        f"{fvg.end_time if fvg else None} | "
                        f"FVG_STATUS={fvg.status if fvg else None}"
                    )
            target_obs = [
                ob
                for ob in context.orderblocks
                if ob.time == target_ob_time
            ]

            print(
                f"{snapshot_time} | "
                f"df_first={context.df['time'].iloc[0]} | "
                f"df_last={context.df['time'].iloc[-1]} | "
                f"FVG={len(context.fvgs)} | "
                f"OB={len(context.orderblocks)} | "
                f"TARGET_OB_16:09={len(target_obs)}"
            )

            for ob in target_obs:
                fvg = ob.related_fvg

                print(
                    "    TARGET OB FOUND | "
                    f"direction={'BUY' if ob.bullish else 'SELL'} | "
                    f"mitigated={ob.mitigated} | "
                    f"status={ob.status} | "
                    f"OB_ZONE={ob.expanded_low} -> {ob.expanded_high} | "
                    f"FVG="
                    f"{fvg.start_time if fvg else None}"
                    f" -> "
                    f"{fvg.end_time if fvg else None} | "
                    f"FVG_STATUS={fvg.status if fvg else None}"
                )

    finally:
        mt5.shutdown()

if __name__ == "__main__":
    main()