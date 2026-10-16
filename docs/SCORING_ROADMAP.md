# Scoring Roadmap

## Purpose

Define a staged implementation plan for a reliable, explainable, and testable signal scoring system.

Scoring must prioritize signal quality without changing the underlying trade-entry rules unintentionally. Each stage should be validated before proceeding to the next stage.

## Baseline and Current State

- Repository: `hqorbani/smartmoney`
- Branch: `main`
- Baseline reference: `feb39ec`
- The main branch has since received improvements to score calculation, market-structure handling, score logging, ranking, and entry filtering.
- Review the current `main` branch before beginning each implementation stage.

### Current Scoring Components

The scoring system currently includes these rules:

- `OBActiveFVGScore`
- `MarketStructureAlignmentScore`
- `OrderBlockEntryReadinessScore`

The configured rule weights are currently:

- `OB_ACTIVE_FVG_SCORE = 2.0`
- `MARKET_STRUCTURE_ALIGNMENT_SCORE = 2.0`
- `ORDER_BLOCK_ENTRY_READINESS_SCORE = 2.0`

`ScoreEngine` calculates the total score and records a per-rule score breakdown on the signal.

The scheduler logs signal scores, including their breakdown, for diagnostic purposes.

These components are implemented, but their effectiveness as predictors of trade quality has not yet been established through systematic validation.

---

## Stage 1 — Market Structure

**Status: In progress**

### Goals

Establish reliable market-structure information before using it as a scoring input.

### Scope

- Validate swing identification and lifecycle.
- Validate bullish and bearish BOS detection.
- Validate bullish and bearish CHOCH detection.
- Validate protected highs and lows.
- Verify that structure bias transitions correctly between bullish, bearish, transition, and unknown states.
- Verify that BOS and CHOCH can be enabled and disabled independently.
- Ensure repeated scheduler cycles do not generate unintended duplicate structure events.

### Acceptance Criteria

- Unit tests cover bullish and bearish structure scenarios.
- BOS and CHOCH behavior is deterministic for equivalent inputs.
- Protected structure levels are updated consistently.
- Unknown or transitional structure does not incorrectly award directional-alignment points.
- Existing behavior is preserved where no intentional change is specified.

### Remaining Work

- Review edge cases involving consecutive breaks, invalidated swings, and transitions following CHOCH.
- Validate behavior against representative market data, not only synthetic unit-test data.

---

## Stage 2 — Feature Model

**Status: Not started**

### Goals

Provide consistent, explicit market features to the scoring rules.

### Scope

- Define how order blocks (OBs) are represented and validated.
- Define the relationship between OBs and fair value gaps (FVGs).
- Define displacement requirements and how they relate to structure events.
- Track relevant retests and entry-zone state.
- Ensure feature values are derived from available historical data without look-ahead bias.
- Handle missing or invalid market data safely.

### Acceptance Criteria

- Feature definitions are explicit and documented.
- Feature calculations are independently testable.
- Missing data does not produce misleading positive scores.
- Historical calculations do not use future candles.
- Feature state remains consistent across scheduler cycles.

---

## Stage 3 — Setup Score

**Status: Not started**

### Goals

Measure the quality of a potential trading setup independently of immediate entry timing.

### Scope

- Score the quality and validity of the order block.
- Score the relationship between the order block and relevant FVGs.
- Incorporate validated market-structure context.
- Define scoring weights and normalization rules.
- Avoid double-counting correlated features.

### Acceptance Criteria

- Each rule has a clear definition and bounded, predictable output.
- Individual rule contributions are visible in the score breakdown.
- Invalid or incomplete setups cannot receive unjustifiably high scores.
- Unit tests cover positive, negative, boundary, and missing-data cases.
- Total scores are reproducible for equivalent inputs.

---

## Stage 4 — Entry Confirmation Score

**Status: Not started**

### Goals

Evaluate entry readiness separately from setup quality.

### Scope

- Evaluate whether the current price is within the eligible entry zone.
- Evaluate the order block's entry-attempt state.
- Incorporate validated entry-confirmation features.
- Keep setup quality distinct from entry timing.
- Ensure scoring does not bypass existing trade-entry requirements.

### Acceptance Criteria

- Entry readiness is evaluated using current, valid market data.
- Signals outside the eligible entry zone do not receive entry-readiness credit.
- Existing entry-attempt and execution rules remain authoritative.
- Unit tests cover initial entry, subsequent attempts, and unavailable entry zones.
- Scoring remains diagnostic unless an explicit, tested filtering policy is approved.

---

## Stage 5 — Ranking and Filtering

**Status: In progress**

### Implemented

The current implementation includes:

- Configurable minimum-score filtering through `Config.MINIMUM_SCORE`.
- Configurable sorting through `Config.SORT_BY`.
- Configurable sort direction through `Config.SORT_DESCENDING`.
- Configurable result limits through `Config.TOP_SIGNALS`.
- Score-based sorting in `QueryEngine`.
- Per-rule score breakdowns in `ScoreEngine`.
- Scheduler integration with the query configuration.
- Signal-score logging for diagnostics.

Relevant configuration currently includes:

- `SORT_BY = "score"`
- `SORT_DESCENDING = True`
- `TOP_SIGNALS = 5`
- `MINIMUM_SCORE = 0.0`

The current minimum-score setting is permissive and should not be treated as a validated quality threshold.

### Remaining Work

- Add or verify dedicated `QueryEngine` tests for score ordering.
- Test minimum-score filtering, including boundary values.
- Test deterministic behavior for equal scores.
- Verify behavior when optional scoring features are unavailable.
- Confirm that displayed and exported signals follow the configured ranking and limit.
- Analyze score distributions before selecting a meaningful minimum-score threshold.
- Validate whether higher-scoring signals actually correspond to better outcomes.

### Acceptance Criteria

- Sorting and filtering behave deterministically.
- The configured result limit is respected.
- Score thresholds are documented and tested.
- Ranking changes do not unintentionally alter execution safety rules.
- Thresholds are calibrated using historical or forward-test evidence rather than intuition alone.

---

## Stage 6 — Multi-Timeframe Alignment

**Status: Deferred**

### Goals

Incorporate higher-timeframe context without introducing look-ahead bias or inconsistent feature state.

### Scope

- Define the relationship between entry and higher timeframes.
- Evaluate directional alignment across timeframes.
- Define behavior when timeframes disagree.
- Avoid using incomplete higher-timeframe candles where doing so would introduce unstable or future-dependent information.
- Keep timeframe configuration separate from scoring implementation.

### Acceptance Criteria

- Timeframe alignment is independently testable.
- Missing or conflicting higher-timeframe data is handled explicitly.
- Historical evaluation uses only information available at the decision time.
- The feature can be enabled or disabled without breaking existing scoring behavior.

---

## Stage 7 — Validation and Documentation

**Status: Not started**

### Goals

Validate that the scoring system is reliable, explainable, and useful in practice.

### Scope

- Add missing unit and integration tests.
- Run the complete relevant test suite.
- Validate scoring against historical market data.
- Compare score bands with observed trade outcomes.
- Measure false positives and missed opportunities.
- Evaluate the effect of thresholds and weights.
- Document scoring rules, configuration, and known limitations.

### Acceptance Criteria

- Relevant unit and integration tests pass.
- Score breakdowns can explain why a signal received its score.
- Historical evaluation avoids look-ahead bias.
- Changes to weights or thresholds have measurable, documented effects.
- Performance claims are supported by data rather than by the score values alone.

---

## Operational Constraints

- Do not change trade-entry logic unintentionally while implementing scoring.
- Do not treat a high score as a guarantee of a profitable trade.
- Do not use future candle information in scoring or validation.
- Keep scoring rules independently testable.
- Preserve explicit reasons for rejected or filtered signals where practical.
- Keep diagnostic logging separate from console presentation.
- Do not mark a stage complete solely because its code has been merged; verify its acceptance criteria.

## Configuration Notes

The current `main` branch enables M1 in `Config.TIMEFRAMES`; M3 and M5 are commented out.

This configuration differs from any previous assumption that M1, M3, and M5 are enabled. Do not change timeframe settings as part of scoring work without a separate, explicit decision.

Current scoring weights and ranking settings are implementation defaults, not empirically validated optimal values.

## Recommended Next Steps

1. Complete Stage 1 validation using representative market data.
2. Add missing tests for Stage 5 ranking and filtering.
3. Define and document the Stage 2 feature model.
4. Implement and validate setup scoring before introducing additional entry-confirmation scoring.
5. Evaluate score distributions and trade outcomes before tightening minimum-score thresholds.
6. Proceed to multi-timeframe scoring only after the single-timeframe model is stable.

## Status Policy

Use the following meanings consistently:

- **Not started:** Implementation work has not begun.
- **In progress:** Some implementation exists, but acceptance criteria are not fully satisfied.
- **Deferred:** Intentionally postponed until prerequisite work is complete.
- **Complete:** Acceptance criteria have been met and verified.

A merged implementation does not automatically qualify a stage as complete.
