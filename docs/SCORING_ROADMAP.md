# ICT / Smart Money Scoring Roadmap

> Living implementation record. Update this document at every scoring-development stage. Update README after implementation and validation, so it describes verified behavior rather than intentions.

## Purpose and scope

Build a score grounded in Smart Money / ICT concepts. It must rank and prioritize signals as well as support configurable filtering. Do not add unrelated signal factors such as RSI, MACD, moving averages, generic candle patterns/counts, or classic volume. ATR may be used for risk management, not as an independent setup-quality signal.

Preserve the configured M3/M5 timeframes. Do not change timeframe configuration as part of scoring work.

## Agreed scoring model (proposed weights)

These weights are the initial proposal, not a claim that every feature is implemented. Confirm each feature's definition and available data before adding a rule. Avoid double-counting the same evidence.

### 1. Market structure — highest priority

| Feature | Proposed points | Notes |
|---|---:|---|
| Valid BOS in trade direction | +3 | Explicit, direction-aware event |
| CHOCH/MSS in trade direction | +3 | Must be explicitly detected |
| OB originating from BOS | +2 | Requires reliable OB-to-event link |
| OB aligned with HTF structure | +2 | Requires defined HTF context |

### 2. Order Block quality

| Feature | Proposed points | Notes |
|---|---:|---|
| OB caused BOS | +3 | Prevent duplicate counting with structure relation |
| OB with FVG | +2 | Prefer validated direct relationship |
| Fresh / unmitigated OB | +2 | Use lifecycle state |
| First retest | +2 | Requires reliable retest/attempt history |
| OB after strong displacement | +2 | Requires measurable displacement definition |
| OB aligned with HTF structure | +2 | Avoid duplicate counting with structure alignment |
| Repeated tests | -1 to -2 | Define thresholds from observed test count |

### 3. Fair Value Gap quality

| Feature | Proposed points | Notes |
|---|---:|---|
| FVG from strong displacement | +2 | Requires measurable displacement |
| FVG associated with BOS | +3 | Requires explicit event association |
| FVG inside / connected to OB | +2 | Do not count the same OB-FVG relationship twice |
| Fresh / unmitigated FVG | +2 | Use lifecycle state |
| Aligned with market structure | +2 | Direction-aware |
| Filled repeatedly | -2 | Requires repeat mitigation/fill history |
| Very small / weak FVG | -1 | Define a scale-aware threshold |

Illustrative calibration: ordinary FVG around 2; FVG + BOS around 5; FVG + BOS + OB around 7+. These are examples, not guaranteed outputs.

### 4. Premium / Discount

| Feature | Proposed points |
|---|---:|
| Buy in Discount / Sell in Premium | +2 |
| Mid-range | 0 |
| Buy in Premium / Sell in Discount | -2 |

Requires a defined dealing range and source swings.

### 5. Liquidity

| Feature | Proposed points |
|---|---:|
| Liquidity sweep before setup | +3 |
| Sweep followed by MSS/BOS | +3 |
| Clear liquidity target in trade direction | +2 |
| No liquidity event | 0 |
| Trading directly into opposing liquidity | -2 |

Example to support: sell-side sweep → bullish MSS → bullish OB/FVG → BUY. Requires explicit liquidity detection and event sequencing.

### 6. Entry confirmation

Keep this separate from setup quality.

| Feature | Proposed points |
|---|---:|
| Valid rejection after price enters zone | +1 |
| Displacement away from zone | +2 |
| Micro BOS/MSS | +3 |
| New FVG in trade direction | +2 |
| Invalid confirmation | -2 |

**Final Score = Setup Score + Entry Confirmation Score.** Zone proximity/readiness alone is not price-action confirmation; keep those concepts distinct.

### 7. Multi-timeframe alignment (later stage)

| Feature | Proposed points |
|---|---:|
| HTF and LTF aligned | +3 |
| HTF conflicts with LTF direction | -2 |

Defer until HTF context and direction semantics are explicit and tested.

## Repository audit — baseline

Reviewed the main branch at baseline commit `feb39ec`. Verify current HEAD before each implementation stage.

### Existing scoring rules

| Component | Current behavior |
|---|---|
| `smartmoney/scoring/fvg.py` — `ActiveFVGScore` | Returns 1 for an `ACTIVE_FVG` strategy, except when both OB and FVG exist because that pair is handled by the OB rule |
| `smartmoney/scoring/orderblock.py` — `OrderBlockScore` | Returns configured 2 points when signal has an OB and FVG, the OB's `related_fvg` is the same FVG object, and the FVG is ACTIVE |
| `smartmoney/scoring/market_structure.py` — `MarketStructureAlignmentScore` | Returns configured 2 points when current market bias matches BUY/SELL; UNKNOWN and TRANSITION score 0 |
| `smartmoney/scoring/orderblock_entry_readiness.py` — `OrderBlockEntryReadinessScore` | Returns configured 2 points when the OB is ACTIVE, an ENTRY zone exists, current ask/bid is inside it, and the first or second attempt is available |
| `smartmoney/scoring/engine.py` — `ScoreEngine` | Sums discovered rules and rounds the total to 2 decimal places |

Relevant configuration in `smartmoney/config.py`: `OB_ACTIVE_FVG_SCORE = 2.0`, `MARKET_STRUCTURE_ALIGNMENT_SCORE = 2.0`, `ORDER_BLOCK_ENTRY_READINESS_SCORE = 2.0`, `MINIMUM_SCORE = 0.0`, `SORT_BY = "distance"`.

### Data already available

- `MarketStructure`: bias, BOS/CHOCH counters, protected and structural highs/lows.
- `StructureEventType`: confirmed bullish/bearish events, weakness events, and enum values for BOS/CHOCH/BULLISH_BOS/BEARISH_BOS.
- `OrderBlock`: direction, candle OHLC/time/index, expanded zone, related FVG, mitigation fields, lifecycle status, first/second attempt status.
- `FVG`: direction, boundaries, start/end index/time, ACTIVE/MITIGATED/FILLED status, first mitigation and fill fields.
- `MarketContext`: candles, swings, swing relations, structures, FVGs, OBs, market structure, and current bid/ask.
- `QueryEngine` already supports minimum-score filtering and sorting by score.

### Gaps and correctness risks confirmed in the inspected code

* Bullish and bearish BOS detection, counting, and `BULLISH_BOS` / `BEARISH_BOS` event emission are implemented and covered by tests. False-break handling and CHOCH/MSS transition behavior remain outstanding.

* The bullish displacement check is only `close > open`; this is not a robust displacement-strength measure.

* `MarketStructureEngine._handle_transition()` is a placeholder; CHOCH/MSS processing is not implemented there.

* `StructureEventEngine` currently defines bullish weakness with the same HH-HL-HH pattern used for bullish confirmation; bearish weakness also uses that bullish pattern. These definitions are not reliable evidence for scoring and must be corrected and tested.

* BOS events are emitted with their direction, but reliable event metadata and explicit event-to-price/time association still need to be verified and completed.

* OB has mitigation state but no independent retest count. Do not infer repeated retests from a boolean alone.

* FVG stores first mitigation/fill metadata, not complete repeated-fill history.

* No verified dedicated liquidity-sweep or Premium/Discount engine was identified in the reviewed models/context.

* Scheduler currently queries with `minimum_score=0.0` and `sort_by="distance"`. Scores are calculated, but current configuration does not prioritize by score or reject candidates using a meaningful score threshold.

* Entry readiness means price is in the zone and an attempt is available; it does not prove rejection, displacement, or micro-structure confirmation.

## Implementation stages and completion log

Mark a stage complete only after code review and focused tests pass. Record commit SHA(s), test commands/results, and deviations.

### Stage 0 — Baseline audit
- **Status:** Complete (initial audit; revisit if implementation uncovers more dependencies).
- **Result:** Existing models support basic bias alignment, active OB/FVG association, lifecycle state, and entry-zone readiness. Structure-event correctness and several ICT features need development.
- **Baseline:** `feb39ec` (verify HEAD before starting changes).

### Stage 1 — Repair and test structure events / market structure

* **Status:** In progress.
* **Completed:** Corrected bullish and bearish weakness pattern definitions in `StructureEventEngine`; added focused tests for bullish confirmation, bearish confirmation, both weakness patterns, and fewer than three relations. Implemented direction-aware bullish and bearish BOS detection in `MarketStructureEngine`. A detected BOS increments the corresponding counter and emits `BULLISH_BOS` or `BEARISH_BOS`. Added regression tests confirming that repeated processing of the same context does not emit the same BOS event or count it again.
* **Validation:** `pytest -q tests/test_structure_event_engine.py` — 5 passed (earlier validation). `pytest -q tests/test_market_structure_engine.py` — 9 passed after BOS event and duplicate-processing tests. `pytest -q` — 262 passed after the BOS changes. `git diff --check` — clean.
* **Implementation commit:** `ecaaf2f` — `Emit bullish and bearish BOS events`.
* **Remaining:** Implement and test false-break handling, CHOCH/MSS transition behavior, and event metadata sufficient for reliable event-to-price/time association.
* **Scope:** Correct weakness event patterns; implement and test direction-aware bullish and bearish BOS; define CHOCH/MSS transition behavior; emit event details sufficient to associate events with price levels and time.
* **Acceptance:** Unit tests cover bullish and bearish cases, false breaks, transition behavior, and repeated processing without duplicate BOS counting. Event definitions must be explicit and consistent with ICT intent.



### Stage 2 — Feature model and evidence links
- **Status:** Not started.
- **Scope:** Add explicit OB/FVG-to-structure-event links; define measurable displacement; model retest count/history and lifecycle evidence without inferring unrecorded data.
- **Acceptance:** Feature provenance is testable; repeated scans do not inflate counts; no duplicate scoring for the same evidence.

### Stage 3 — Setup score
- **Status:** Not started.
- **Scope:** Add supported market-structure, OB, FVG, Premium/Discount, and liquidity rules in small increments, prioritizing features with reliable source data.
- **Acceptance:** Each rule has focused positive, negative, neutral, missing-data, and direction-mismatch tests; scoring avoids double-counting.

### Stage 4 — Entry confirmation score
- **Status:** Not started.
- **Scope:** Separate actual rejection/displacement/micro-BOS/new-FVG confirmations from mere zone readiness.
- **Acceptance:** Final score equals setup score plus entry-confirmation score; tests verify confirmation is only credited after price enters the relevant zone.

### Stage 5 — Ranking and filtering
- **Status:** Not started.
- **Scope:** Make score-based ranking configurable and establish a configurable minimum score once score semantics are stable. Keep distance optional rather than accidentally primary.
- **Acceptance:** Tests prove ordering, threshold filtering, tie handling, and sensible behavior when optional features are unavailable.

### Stage 6 — Multi-timeframe alignment
- **Status:** Deferred.
- **Scope:** Introduce explicit HTF structure context and tested alignment/conflict scoring.
- **Acceptance:** Tests cover aligned, conflicting, and unknown HTF/LTF cases; no timeframe configuration changes are bundled into this work.

### Stage 7 — Validation and documentation
- **Status:** Not started.
- **Scope:** Run the full test suite and relevant historical/backtest analysis; compare score ranks with outcomes; tune weights only from documented evidence. Then update README to describe implemented scoring and link to this roadmap.
- **Acceptance:** Full test results and known limitations are recorded; README describes only behavior that exists and has been verified.

## Working rules

1. Before a stage, inspect the current branch and relevant code; do not assume this baseline is still HEAD.
2. Implement one coherent stage at a time with focused regression tests.
3. Update this file in the same change/commit as each stage's implementation, including status, findings, test results, and commit SHA when available.
4. Never mark a feature as implemented merely because a model field or enum exists.
5. Avoid duplicate points for one event or relationship.
6. Keep the strategy ICT/SMC-grounded; do not introduce unrelated indicators as scoring factors.
7. Do not change configured timeframes as part of this roadmap.
8. Update README after scoring is implemented and validated, summarizing current behavior and linking here for detailed progress.
