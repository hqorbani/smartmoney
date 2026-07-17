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