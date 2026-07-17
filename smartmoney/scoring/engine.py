class ScoreEngine:

    def __init__(self):

        self.rules = []

    def add(self, rule):

        self.rules.append(rule)

    def calculate(self, signal, context):

        score = 0.0

        for rule in self.rules:

            score += rule.score(signal, context)

        signal.score = round(score, 2)

        return signal