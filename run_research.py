from pathlib import Path

from smartmoney.backtesting.orderblock_diagnostics import (
    analyze_orderblock_diagnostics,
)
from smartmoney.backtesting.research import HistoricalResearchRunner
from smartmoney.backtesting.trade_export import (
    export_backtest_trade_details_to_excel,
)
from smartmoney.config import Config
from smartmoney.core.mt5 import MT5DataProvider


def main() -> None:
    provider = MT5DataProvider()

    for timeframe in Config.TIMEFRAMES:
        runner = HistoricalResearchRunner(
            symbol="NAS100",
            timeframe=timeframe,
        )

        result = runner.run_from_provider(
            provider=provider,
            candle_count=Config.HISTORY_BARS,
        )
        if Config.EXPORT_BACKTEST_TRADE_DETAILS:
            output_path = (
                Path("exports")
                / f"NAS100_TF_{timeframe}_backtest_trades.xlsx"
            )

            export_backtest_trade_details_to_excel(
                result=result,
                output_path=output_path,
            )

            print(
                f"Trade details exported to: {output_path}"
            )
        diagnostics = analyze_orderblock_diagnostics(
            trades=result.trades,
            candle_count=result.candle_count,
        )

        print(f"\n{'=' * 60}")
        print(f"NAS100 | timeframe={timeframe}")
        print(f"candles={result.candle_count}")
        print(f"trades={len(result.trades)}")

        for zone, stats in result.zone_stats.items():
            print(
                zone.value,
                f"touches={stats.touches}",
                f"frequency={stats.zone_frequency:.2%}",
                f"1R win={stats.win_rate_1r:.2%}",
                f"1R resolution={stats.resolution_rate_1r:.2%}",
                f"2R win={stats.win_rate_2r:.2%}",
                f"2R resolution={stats.resolution_rate_2r:.2%}",
                f"penetration={stats.average_penetration:.2%}",
                f"max_penetration={stats.average_max_ob_penetration:.2%}",
            )

            diagnostic = diagnostics[zone]

            print(
                f"  zero-risk={diagnostic.zero_risk_touches}",
                f"resolved_1r={diagnostic.resolved_1r}",
                f"unresolved_1r={diagnostic.unresolved_1r}",
                f"last10={diagnostic.unresolved_1r_last_10}",
                f"last20={diagnostic.unresolved_1r_last_20}",
                f"last50={diagnostic.unresolved_1r_last_50}",
                f"last100={diagnostic.unresolved_1r_last_100}",
            )

            print(
                f"  resolved_2r={diagnostic.resolved_2r}",
                f"unresolved_2r={diagnostic.unresolved_2r}",
                f"last10_2r={diagnostic.unresolved_2r_last_10}",
                f"last20_2r={diagnostic.unresolved_2r_last_20}",
                f"last50_2r={diagnostic.unresolved_2r_last_50}",
                f"last100_2r={diagnostic.unresolved_2r_last_100}",
            )


if __name__ == "__main__":
    main()