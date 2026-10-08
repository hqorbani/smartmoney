from smartmoney.scoring.base import ScoreRule


class ActiveFVGScore(ScoreRule):
    def score(self, signal, context):
        # OB + FVG is scored by OrderBlockScore.
        if signal.orderblock is not None and signal.fvg is not None:
            return 0.0

        if "ACTIVE_FVG" in (signal.strategy or ""):
            return 1.0

        return 0.0