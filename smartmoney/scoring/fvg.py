from smartmoney.scoring.base import ScoreRule


class ActiveFVGScore(ScoreRule):

    def score(self, signal, context):

        if "ACTIVE_FVG" in signal.strategy:

            return 1.0

        return 0.0