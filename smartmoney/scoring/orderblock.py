from smartmoney.scoring.base import ScoreRule


class OrderBlockScore(ScoreRule):

    def score(self, signal, context):

        if "OB" in signal.strategy:

            return 1.0

        return 0.0