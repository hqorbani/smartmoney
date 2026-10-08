from smartmoney.config import Config
from smartmoney.models.market_structure import MarketBias
from smartmoney.scoring.base import ScoreRule


class MarketStructureAlignmentScore(ScoreRule):
    def score(self, signal, context):
        bias = context.market_structure.bias
        if bias == MarketBias.UNKNOWN:
            return 0.0

        if bias == MarketBias.TRANSITION:
            return 0.0

        if signal.direction == "BUY":
            if bias == MarketBias.BULLISH:
                return Config.MARKET_STRUCTURE_ALIGNMENT_SCORE
            return 0.0

        if signal.direction == "SELL":
            if bias == MarketBias.BEARISH:
                return Config.MARKET_STRUCTURE_ALIGNMENT_SCORE
            return 0.0

        return 0.0