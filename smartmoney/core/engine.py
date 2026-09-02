class AnalyzerEngine:

    def __init__(self):
        self._analyzers = []

    def add(self, analyzer):
        self._analyzers.append(analyzer)
        self._analyzers.sort(key=lambda x: x.priority)

    def run(self, context):

        for analyzer in self._analyzers:
            analyzer.analyze(context)

        return context

    def run_from_priority(self, context, priority):
        for analyzer in self._analyzers:
            if analyzer.priority >= priority:
                analyzer.analyze(context)

        return context