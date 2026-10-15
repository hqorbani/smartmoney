
from types import SimpleNamespace

from smartmoney.scoring.engine import ScoreEngine


class FixedScoreRule:
    def __init__(self, value):
        self.value = value
        self.calls = 0

    def score(self, signal, context):
        self.calls += 1
        return self.value


def test_score_engine_records_breakdown_and_preserves_total():
    engine = ScoreEngine()
    first_rule = FixedScoreRule(2.0)
    second_rule = FixedScoreRule(1.5)
    engine.add(first_rule)
    engine.add(second_rule)

    signal = SimpleNamespace(score=0.0)
    context = SimpleNamespace()

    result = engine.calculate(signal, context)

    assert result is signal
    assert signal.score == 3.5
    assert signal.score_breakdown == {
        "FixedScoreRule": 2.0,
        "FixedScoreRule_2": 1.5,
    }
    assert first_rule.calls == 1
    assert second_rule.calls == 1


def test_score_engine_handles_no_rules():
    engine = ScoreEngine()
    signal = SimpleNamespace(score=99.0)

    result = engine.calculate(signal, SimpleNamespace())

    assert result is signal
    assert signal.score == 0.0
    assert signal.score_breakdown == {}
