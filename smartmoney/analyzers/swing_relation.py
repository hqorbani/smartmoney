from smartmoney.analyzers.base import Analyzer

from smartmoney.models.swing import Swing
from smartmoney.models.swing_relation import (
    SwingRelation,
    SwingRelationType,
)


class SwingRelationAnalyzer(Analyzer):

    priority = 20

    def analyze(self, context):

        context.swing_relations.clear()

        last_high: Swing | None = None
        last_low: Swing | None = None

        for swing in context.swings:

            if swing.is_high:

                if last_high is None:

                    last_high = swing
                    continue

                relation = (
                    SwingRelationType.HIGHER_HIGH
                    if swing.price > last_high.price
                    else SwingRelationType.LOWER_HIGH
                )

                context.swing_relations.append(
                    SwingRelation(
                        previous=last_high,
                        current=swing,
                        relation=relation,
                    )
                )

                last_high = swing

            else:

                if last_low is None:

                    last_low = swing
                    continue

                relation = (
                    SwingRelationType.HIGHER_LOW
                    if swing.price > last_low.price
                    else SwingRelationType.LOWER_LOW
                )

                context.swing_relations.append(
                    SwingRelation(
                        previous=last_low,
                        current=swing,
                        relation=relation,
                    )
                )

                last_low = swing

        # ---------- TEMP DEBUG ----------
        # print()
        # print(f"{context.symbol} {context.timeframe}")
        # print(f"Relations : {len(context.swing_relations)}")

        # for relation in context.swing_relations[-10:]:

        #     print(
        #         relation.relation.value,
        #         relation.current.time,
        #         f"{relation.current.price:.5f}",
        #     )