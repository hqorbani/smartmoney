from smartmoney.config import Config
from smartmoney.models.fvg import FVGStatus
from smartmoney.scoring.base import ScoreRule


class OrderBlockScore(ScoreRule):
    def score(self, signal, context):
        orderblock = signal.orderblock
        fvg = signal.fvg

        if orderblock is None or fvg is None:
            return 0.0

        if orderblock.related_fvg is not fvg:
            return 0.0

        if fvg.status != FVGStatus.ACTIVE:
            return 0.0

        return Config.OB_ACTIVE_FVG_SCORE