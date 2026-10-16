
from smartmoney.config import Config
from smartmoney.models.market_structure import MarketBias
from smartmoney.models.signal import SignalDirection
from smartmoney.scoring.base import ScoreRule


class MarketStructureAlignmentScore(ScoreRule):
    def score(self, signal, context):
        bias = context.market_structure.bias

        if bias in (MarketBias.UNKNOWN, MarketBias.TRANSITION):
            return 0.0

        direction = signal.direction

        if isinstance(direction, SignalDirection):
            direction = direction.value

        if isinstance(direction, str):
            direction = direction.upper()

        if direction == "BUY" and bias == MarketBias.BULLISH:
            return Config.MARKET_STRUCTURE_ALIGNMENT_SCORE

        if direction == "SELL" and bias == MarketBias.BEARISH:
            return Config.MARKET_STRUCTURE_ALIGNMENT_SCORE

        return 0.0
