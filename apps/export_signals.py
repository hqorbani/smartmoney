from smartmoney.bootstrap import create_provider, create_signal_scanner
from smartmoney.outputs.csv_output import CsvOutput


def main() -> None:
    provider = create_provider()
    provider.connect()

    try:
        scanner = create_signal_scanner(provider)
        signals = scanner.scan()

        CsvOutput().publish(signals)

        print(f"Exported {len(signals)} signals to outputs/signals.csv")

    finally:
        provider.shutdown()


if __name__ == "__main__":
    main()