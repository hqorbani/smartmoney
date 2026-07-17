from smartmoney.models.signal import Signal


class ScannerEngine:

    def __init__(self):

        self.scanners = []

    def add(self, scanner):

        self.scanners.append(scanner)

    def run(self, context) -> list[Signal]:

        signals = []

        for scanner in self.scanners:

            signals.extend(scanner.scan(context))

        return signals