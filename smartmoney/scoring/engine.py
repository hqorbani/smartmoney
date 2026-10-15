
class ScoreEngine:

    def __init__(self):
        self.rules = []

    def add(self, rule):
        self.rules.append(rule)

    def calculate(self, signal, context):
        score = 0.0
        breakdown = {}

        for index, rule in enumerate(self.rules):
            rule_score = rule.score(signal, context)
            score += rule_score

            rule_name = rule.__class__.__name__
            if rule_name in breakdown:
                rule_name = f"{rule_name}_{index + 1}"

            breakdown[rule_name] = round(rule_score, 2)

        signal.score_breakdown = breakdown
        signal.score = round(score, 2)

        return signal
