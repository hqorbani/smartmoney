from smartmoney.core.engine import AnalyzerEngine


class FirstAnalyzer:

    priority = 30

    def analyze(self, context):
        context.execution_order.append("first")


class SecondAnalyzer:

    priority = 10

    def analyze(self, context):
        context.execution_order.append("second")


class ThirdAnalyzer:

    priority = 20

    def analyze(self, context):
        context.execution_order.append("third")


class DummyContext:

    def __init__(self):
        self.execution_order = []


def test_analyzer_engine_executes_analyzers_in_priority_order():

    engine = AnalyzerEngine()

    engine.add(FirstAnalyzer())
    engine.add(SecondAnalyzer())
    engine.add(ThirdAnalyzer())

    context = DummyContext()

    engine.run(context)

    assert context.execution_order == [
        "second",
        "third",
        "first",
    ]