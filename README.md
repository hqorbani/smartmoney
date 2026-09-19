# SmartMoney

Smart Money Concepts (SMC) trading analysis framework for MetaTrader 5.

SmartMoney is a modular Python project for detecting and evaluating SMC/ICT-style market structures and trade opportunities. The system separates market data, domain models, analysis, scanning, scoring, querying, visualization, and application orchestration so that each part can evolve independently.

> **Current branch:** `main`  

---
## 1. Project Purpose

The project is being developed as a reusable market-analysis and trading framework rather than as a single hard-coded trading script.

The intended architecture allows the project to grow toward:

* Market structure analysis
* Swing analysis
* Fair Value Gap (FVG) detection and lifecycle management
* Order Block detection
* Structure events
* Signal generation
* Entry validation
* Stop-loss calculation
* Take-profit calculation
* Risk/reward calculation
* Position sizing
* Broker-aware position sizing
* Signal scoring
* Multi-timeframe analysis
* Historical signal evaluation
* Backtesting
* MetaTrader 5 trade execution
* Position management

The current system is primarily an **analysis and signal-generation system**, with a separate MT5 execution layer that has been implemented and validated on a Demo account.

**Automatic execution is not yet connected to the main Live analysis pipeline.**

---

## 2. Current Capabilities

### Market Data

* MetaTrader 5 integration
* Multi-symbol analysis
* Multi-timeframe analysis
* Historical candle retrieval
* Current market-price retrieval
* Account-balance retrieval
* Removal of the incomplete/latest candle before analysis

### Market Analysis

* Swing detection
* Swing relationships
* Fair Value Gap detection
* FVG lifecycle management
* Order Block detection
* Structure analysis
* Market structure state
* Structure events

### Signal and Strategy Pipeline

* Signal generation
* Active FVG scanning
* Order Block + Active FVG scanning
* Entry validation
* Stop-loss planning
* Take-profit planning
* Trade-plan generation
* Generic position-size planning

### MT5 Execution

The project now contains a dedicated MetaTrader 5 execution layer.

Current capabilities include:

* MT5 order request construction
* Broker-aware MT5 volume calculation
* MT5 order validation through `order_check`
* MT5 market-order execution
* Demo position opening
* Demo position closing
* Broker result handling
* Execution status/result abstraction

The Demo execution path has been validated against a real MetaTrader 5 Demo account.

The execution layer is currently available as infrastructure but is **not yet automatically triggered by the main Live scanner pipeline**.

---
# 3. High-Level Architecture

The project is divided into several layers.

```text
                         ┌─────────────────────┐
                         │    MetaTrader 5     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    MT5DataProvider  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      Scheduler      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   ContextManager    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   AnalyzerEngine    │
                         └──────────┬──────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
        Swing/FVG             Order Block              Structure
        Analysis              Analysis                 Analysis
             │                      │                      │
             └──────────────────────┼──────────────────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ StructureEventEngine│
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ MarketStructureEngine│
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   ScannerEngine     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                           Scanner-generated
                              Signals
                                    │
                                    ▼
                     ┌───────────────────────────┐
                     │ Per-Signal Trade Pipeline │
                     └─────────────┬─────────────┘
                                   │
                 ┌─────────────────┼─────────────────┐
                 ▼                 ▼                 ▼
               Entry              SL                TP
                 │                 │                 │
                 └─────────────────┼─────────────────┘
                                   ▼
                              Trade Plan
                                   │
                                   ▼
                             Position Size
                                   │
                                   ▼
                            Score Engine
                                   │
                                   ▼
                          Distance Service
                                   │
                                   ▼
                         Signal Repository
                                   │
                                   ▼
                             Query Engine
                                   │
                                   ▼
                            Output / Display
```

---

# 4. Runtime Flow

The analysis application processes each configured symbol and timeframe independently.

The current analysis sequence is:

```text
1. Connect to MT5
2. Fetch market data
3. Remove the incomplete candle
4. Create/update MarketContext
5. Run analyzers
6. Generate structure events
7. Update market structure
8. Run scanners
9. Process each scanner signal
10. Build downstream trade plans when applicable
11. Calculate position-size plan
12. Calculate score
13. Calculate distance from current price
14. Store signals in repository
15. Apply query filters/sorting/limit
16. Publish the resulting signals
17. Repeat after the configured scan interval
```

The application is orchestrated by:

```text
smartmoney/core/scheduler.py
smartmoney/bootstrap.py
```

### Execution Flow

The MT5 execution layer is currently separate from the automatic Live pipeline.

When explicitly invoked, the execution path is:

```text
TradePlan
    ↓
Broker-aware MT5 volume
    ↓
MT5 Order Request
    ↓
MT5 Order Check
    ↓
MT5 Order Send
    ↓
Opened Position
    ↓
Position Close Request
    ↓
MT5 Order Send
    ↓
Closed Position
```

The Demo execution path has been successfully validated for both opening and closing a position.

Automatic execution from a Live-generated `TradePlan` remains a future integration step.

---


# 5. Application Entry Points

### Live Scanner

```bash
python -m apps.live
```

The Live application runs the market-analysis loop against MetaTrader 5.

It currently constructs and runs the analysis pipeline.

**It does not automatically send trading orders from scanner-generated trade plans yet.**

### Demo Order Execution

```bash
python -m apps.demo_order
```

The Demo order application provides a controlled manual entry point for validating MT5 order execution.

It is intended for Demo-account execution testing and should not be considered the production Live trading entry point.

### Chart Application

```bash
python -m apps.chart
```

The chart application uses the visualization layer to display market data and analysis.

---

# 6. MarketContext

`MarketContext` is the central state object for a single symbol/timeframe analysis.

It contains the market data and intermediate results required by different stages.

Conceptually:

```text
MarketContext
│
├── symbol
├── timeframe
├── df
├── last_candle_time
│
├── swings
├── structures
├── fvgs
├── orderblocks
│
├── signal
├── entry_plan
├── stop_loss_plan
├── take_profit_plan
├── trade_plan
├── position_size_plan
│
├── market_structure
└── swing_relations
```

The purpose of `MarketContext` is to provide a shared analysis state without forcing analyzers to directly depend on one another.

---

# 7. Analyzer Architecture

Analyzers implement individual pieces of market analysis or downstream trade-plan construction.

The analyzer base abstraction is located at:

```text
smartmoney/analyzers/base.py
```

Analyzers are discovered dynamically by the bootstrap/discovery mechanism and registered with `AnalyzerEngine`.

## Analyzer priorities

Analyzer priority defines execution order and therefore expresses dependencies between stages.

The current downstream trade-plan sequence is:

```text
FVG
 ↓
Order Block
 ↓
Signal
 ↓
Entry
 ↓
Stop Loss
 ↓
Take Profit
 ↓
Trade Plan
 ↓
Position Size
```

Structure-related analyzers and engines operate as part of the broader market-structure pipeline.

## AnalyzerEngine

Located at:

```text
smartmoney/core/engine.py
```

The engine provides:

```python
run(context)
```

to execute the complete analyzer pipeline.

It also provides:

```python
run_from_priority(context, priority)
```

to execute only analyzers whose priority is greater than or equal to the requested priority.

The second mode is important for scanner-generated signals because a scanner may already know the relevant Order Block/FVG and only the downstream trade-plan stages need to be executed for that specific signal.

---

# 8. Scanner Architecture

Scanners search the analyzed `MarketContext` for opportunities.

Scanner abstractions are located in:

```text
smartmoney/scanners/
```

Current scanners:

## Active FVG

File:

```text
smartmoney/scanners/active_fvg.py
```

Detects FVGs whose lifecycle status is `ACTIVE`.

## Order Block + Active FVG

File:

```text
smartmoney/scanners/orderblock_active_fvg.py
```

Detects Order Blocks that are associated with an active FVG.

This scanner produces a signal containing the relevant Order Block and FVG so that downstream trade-plan analysis can operate on that specific setup.

## Scanner Registry

File:

```text
smartmoney/scanners/registry.py
```

Scanner registration/discovery is kept separate from the individual scanner implementations.

---

# 9. Signal Model

The signal domain model is:

```text
smartmoney/models/signal.py
```

A signal can represent:

- Symbol
- Timeframe
- Strategy
- Direction
- Price range
- Timestamp
- Score
- Distance
- Current price
- Reason
- Order Block
- FVG

The signal model is intentionally kept lightweight.

Trade-plan models are separate domain objects and should not be imported into `Signal` merely to make them fields of the signal model.

The current architecture uses the analysis context for plan creation and can attach generated plan objects to scanner signals without creating direct model-import cycles.

---

# 10. Trade Plan Pipeline

A scanner signal does not automatically mean that a trade is ready.

The current strategy intentionally separates:

```text
Opportunity Detection
```

from:

```text
Entry Activation
```

The pipeline is:

```text
Scanner Signal
      │
      ▼
Order Block + FVG
      │
      ▼
Wait for price to reach/touch Order Block
      │
      ▼
Entry Plan
      │
      ▼
Stop Loss Plan
      │
      ▼
Take Profit Plan
      │
      ▼
Trade Plan
      │
      ▼
Position Size Plan
```

## Entry rule

The current Entry Analyzer creates an Entry Plan only when the current candle reaches or touches the relevant Order Block.

Therefore:

```text
Active FVG + Order Block
        ≠
Immediate Entry
```

An active setup can exist without an active trade plan.

This behavior is intentional and should not be changed unless the strategy itself is intentionally changed.

---

# 11. Entry Plan

File:

```text
smartmoney/analyzers/entry.py
```

Model:

```text
smartmoney/models/entry.py
```

The current implementation uses the midpoint of the Order Block as the entry price:

```text
Entry = (OB High + OB Low) / 2
```

An Entry Plan requires:

- A valid BUY or SELL signal
- An Order Block
- An FVG
- Non-empty market data
- Current price/candle interaction with the Order Block

If price has not reached the Order Block, no Entry Plan is produced.

---

# 12. Stop Loss Plan

Files:

```text
smartmoney/analyzers/stoploss.py
smartmoney/models/stoploss.py
```

For a BUY:

```text
SL = Order Block Low
```

For a SELL:

```text
SL = Order Block High
```

The analyzer validates that the resulting stop is on the correct side of the entry.

A Stop Loss Plan is created only when a valid Entry Plan exists.

---

# 13. Take Profit Plan

Files:

```text
smartmoney/analyzers/takeprofit.py
smartmoney/models/takeprofit.py
```

Take profit is derived from risk and the configured risk/reward ratio.

For BUY:

```text
TP = Entry + (Risk × RR)
```

For SELL:

```text
TP = Entry - (Risk × RR)
```

The configured ratio is read from:

```text
smartmoney/config.py
```

through:

```python
Config.RR_RATIO
```

---

# 14. Trade Plan

Files:

```text
smartmoney/analyzers/tradeplan.py
smartmoney/models/tradeplan.py
```

A Trade Plan combines:

- Direction
- Entry price
- Stop loss
- Take profit
- Risk
- Reward
- Risk/reward ratio

The Trade Plan is created only after the required upstream stages have succeeded.

---

## 15. Position Size

### Generic Position Size Planning

Files:

```text
smartmoney/analyzers/position_size.py
smartmoney/models/position_size.py
```

The generic position-size calculation uses:

```text
Account Balance
        ×
Risk Percentage
        ↓
Risk Amount
        ÷
Stop Distance
        ↓
Position Size Plan
```

This layer remains broker-independent.

### MT5 Broker-Aware Volume

The MT5 execution layer converts the generic risk information into a broker-compatible MT5 volume.

File:

```text
smartmoney/trading/mt5_volume.py
```

The MT5 calculation considers:

* Risk amount
* Stop distance
* Tick value
* Tick size
* Volume step
* Minimum volume
* Maximum volume

Conceptually:

```text
Risk Amount
     ↓
Stop Distance
     ↓
Tick Value / Tick Size
     ↓
Raw MT5 Volume
     ↓
Broker Volume Step
     ↓
Validated MT5 Volume
```

This separation keeps the generic position-size model independent from broker-specific contract rules.

---

# 16. Market Structure

Market-structure functionality is distributed between analyzers, domain models, and core engines.

Important files include:

```text
smartmoney/analyzers/structure.py
smartmoney/analyzers/swing.py
smartmoney/analyzers/swing_relation.py

smartmoney/models/market_structure.py
smartmoney/models/structure.py
smartmoney/models/structure_event.py
smartmoney/models/structure_level.py
smartmoney/models/swing.py
smartmoney/models/swing_relation.py

smartmoney/core/market_structure_engine.py
smartmoney/core/structure_event_engine.py
```

The project keeps structural analysis separate from scanner and output concerns.

---

# 17. FVG Lifecycle

FVG functionality is split between detection and lifecycle management.

Important files:

```text
smartmoney/analyzers/fvg.py
smartmoney/analyzers/fvg_lifecycle.py
smartmoney/models/fvg.py
```

The lifecycle distinguishes states such as:

```text
ACTIVE
MITIGATED
FILLED
```

Scanners that specifically require an active FVG must check the FVG lifecycle state rather than assuming that every detected FVG remains actionable.

---

# 18. Scoring

Scoring is implemented under:

```text
smartmoney/scoring/
```

Files currently include:

```text
base.py
engine.py
fvg.py
orderblock.py
```

The Score Engine combines rule-based scoring components.

Scoring should evaluate an already-generated signal.

It should not be responsible for:

- Detecting FVGs
- Detecting Order Blocks
- Creating entries
- Creating stop losses
- Creating take profits
- Executing trades

This separation keeps scoring independent from market-detection logic.

---

# 19. Distance Service

File:

```text
smartmoney/services/distance_service.py
```

The Distance Service calculates the relationship between a signal and the current market price.

Distance calculation is kept separate from:

- Signal detection
- Trade-plan generation
- Scoring
- Output formatting

---

# 20. Repository

Files:

```text
smartmoney/repository/__init__.py
smartmoney/repository/signal_repository.py
```

`SignalRepository` stores the signals produced during a scheduler cycle.

Its responsibilities include:

- Replacing the current signal collection
- Adding individual signals
- Returning stored signals
- Clearing signals
- Counting signals

The repository is intentionally separate from signal generation and querying.

---

# 21. Query Layer

Files:

```text
smartmoney/query/query.py
smartmoney/query/query_engine.py
```

The Query layer operates on generated signals.

It is responsible for applying requirements such as:

- Minimum score
- Sort field
- Sort direction
- Result limit

The Query layer should not create or modify trading signals.

---

# 22. Visualization

Visualization is located under:

```text
smartmoney/visualization/
```

Current visualization component:

```text
smartmoney/visualization/chart.py
```

The chart application is started through:

```bash
python -m apps.chart
```

Visualization should consume analysis results rather than becoming another place where trading logic is implemented.

---

# 23. Bootstrap and Dependency Assembly

The application composition root is:

```text
smartmoney/bootstrap.py
```

Bootstrap is responsible for constructing and connecting the main application components.

It creates or discovers:

- MT5 provider
- Context manager
- Analyzer Engine
- Scanner Engine
- Score Engine
- Output Engine
- Market Structure Engine
- Structure Event Engine
- Signal Repository
- Query Engine
- Distance Service
- Position Size Analyzer
- Scheduler

The bootstrap layer is where infrastructure and implementations are assembled.

Business logic should not be duplicated inside bootstrap.

---

# 24. Dynamic Discovery

The discovery mechanism is implemented through:

```text
smartmoney/core/discovery.py
```

The project uses discovery for extensible components such as:

- Analyzers
- Scanners
- Score rules
- Outputs

The general idea is:

```text
Package
   ↓
Discover subclasses
   ↓
Instantiate/register
   ↓
Engine
```

This allows new implementations to be added without requiring the core engine to know every concrete class in advance.

---

# 25. Configuration

Main configuration:

```text
smartmoney/config.py
```

Configuration includes runtime parameters such as:

- Symbols
- Timeframes
- Historical candle count
- Scan interval
- Risk percentage
- Risk/reward ratio
- Minimum score
- Sorting configuration
- Maximum number of returned signals

Global runtime parameters should normally live in `Config` rather than being hard-coded in business logic.

---

# 26. Data Provider

The MetaTrader 5 market-data integration is implemented through the MT5 provider/client layer.

Market-data responsibilities include:

* Connection
* Shutdown
* Historical rates
* Current price
* Account balance
* Symbol selection
* Market access

The execution layer is intentionally separated from market-data responsibilities.

Execution-specific MT5 functionality is implemented under:

```text
smartmoney/trading/
```

---

# 27. Project Structure

The current repository includes the following major areas:

```text
smartmoney/
│
├── apps/
│   ├── live.py
│   ├── chart.py
│   └── demo_order.py
│
├── smartmoney/
│   ├── analyzers/
│   ├── core/
│   ├── models/
│   ├── query/
│   ├── repository/
│   ├── scanners/
│   ├── scoring/
│   ├── services/
│   ├── trading/
│   ├── visualization/
│   ├── bootstrap.py
│   └── config.py
│
├── tests/
│
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

### Trading Execution Layer

The trading package currently contains components for:

```text
smartmoney/trading/
├── broker_executor.py
├── execution.py
├── mt5_broker_executor.py
├── mt5_client.py
├── mt5_order_request.py
├── mt5_volume.py
├── position_size.py
└── trade_plan.py
```

Responsibilities include:

* Execution abstractions
* Broker execution
* MT5 client access
* MT5 order-request construction
* MT5 volume conversion
* Position execution
* Position closing
* Trade-plan and position-size integration

---

# 28. Layer Responsibilities

A developer extending the project should generally use the following rules.

| Layer | Responsibility |
|---|---|
| `apps/` | Application entry points |
| `core/` | Orchestration, context, discovery, engines, scheduling, infrastructure |
| `models/` | Domain data structures |
| `analyzers/` | Market analysis and downstream plan calculations |
| `scanners/` | Finding candidate opportunities |
| `scoring/` | Signal scoring |
| `services/` | Independent reusable domain/application services |
| `repository/` | Signal storage |
| `query/` | Signal filtering and sorting |
| `visualization/` | Chart presentation |
| `tests/` | Behavioral verification |

Avoid putting the same responsibility into multiple layers.

---

# 29. Testing

The project uses `pytest`.

Run all tests with:

```bash
pytest -q
```

Focused tests can be run individually, for example:

```bash
pytest -q tests/test_mt5_broker_executor.py
```

The repository currently contains tests covering both analysis and execution components, including:

* Analyzer execution
* Historical backtesting
* Order Block research
* Entry
* Full pipeline
* FVG
* FVG lifecycle
* Order Block
* Pipeline
* Position sizing
* Signal
* Stop loss
* Take profit
* Trade plan
* MT5 client behavior
* MT5 integration
* MT5 order requests
* MT5 broker execution
* MT5 volume conversion
* Demo order helpers

The MT5 Demo execution path has been manually validated for:

* Opening a Demo position
* Closing the opened Demo position

Production/live trading must not be considered validated solely from these Demo-account tests.

---

# 30. Development Rules

## Rule 1 — Preserve separation of responsibilities

Do not move business logic into:

- Output classes
- Application entry points
- Bootstrap
- Repository
- Query layer

unless that logic genuinely belongs there.

## Rule 2 — Respect analyzer dependencies

If an analyzer depends on the result of another analyzer, its priority must execute it afterward.

## Rule 3 — Use MarketContext for shared analysis state

Do not create unnecessary direct dependencies between analyzers.

## Rule 4 — Keep domain models independent

Avoid importing unrelated domain models into each other merely for convenience.

Especially avoid creating circular dependencies between signal and trade-plan models.

## Rule 5 — Add tests with behavior changes

A strategy-rule change should be accompanied by tests that explicitly verify the new behavior.

## Rule 6 — Do not silently change trading semantics

Changes such as:

- Entry activation rules
- FVG lifecycle behavior
- Order Block selection
- SL placement
- TP calculation
- Position sizing
- Signal direction

are strategy changes and should be treated as intentional design decisions.

## Rule 7 — Update documentation with architecture changes

When the architecture changes, update this README and the detailed documentation associated with that component.

---

# 31. Current Strategy Semantics

The current strategy intentionally distinguishes between a detected opportunity and an executable trade setup.

```text
Detected Setup
      ↓
Scanner Signal
      ↓
Price reaches/touches Order Block
      ↓
Entry Plan
      ↓
SL / TP
      ↓
Trade Plan
      ↓
Position Size
```

Therefore, a scanner can legitimately produce a signal without producing:

- Entry Plan
- Stop Loss Plan
- Take Profit Plan
- Trade Plan
- Position Size Plan

This is not an error when the entry condition has not been met.

---

# 32. Risk Management Semantics

The generic risk-management flow is:

```text
Account Balance
       ↓
Configured Risk %
       ↓
Risk Amount
       ↓
Stop Distance
       ↓
Position Size Plan
```

For MT5 execution, the generic risk information is converted into broker-compatible volume using instrument-specific information:

* Tick size
* Tick value
* Volume step
* Minimum volume
* Maximum volume

The generic analyzer and the MT5-specific converter are intentionally separate.

---

# 33. Repository Consistency Note

The GitHub tree for commit `632b5c1540f6374801d45cadd50e08555ed088ad` currently shows the following top-level directories:

```text
apps/
smartmoney/
tests/
```

and the `smartmoney/` package contains:

```text
analyzers/
core/
models/
query/
repository/
scanners/
scoring/
services/
visualization/
```

The same commit's `smartmoney/bootstrap.py` imports:

```python
smartmoney.outputs.base
smartmoney.outputs.output_engine
```

but the GitHub tree currently does not expose a `smartmoney/outputs/` directory.

This discrepancy should be resolved in the repository before considering the GitHub commit a fully reproducible clean checkout.

Until that is resolved, documentation should not pretend that the repository is completely self-contained if a fresh clone cannot construct the Output Engine.

---

# 34. Roadmap

### Completed

* MT5 market-data integration
* Generic position-size planning
* MT5 broker-aware volume conversion
* MT5 order request construction
* MT5 order validation
* MT5 broker execution abstraction
* Demo position opening
* Demo position closing
* Demo execution result handling

### Current / Near Term

* Connect generated `TradePlan` objects to the MT5 execution layer
* Define automatic execution safeguards
* Add position lifecycle tracking
* Add duplicate-position protection
* Improve execution error handling
* Improve broker-specific execution validation
* Resolve remaining repository/documentation inconsistencies

### Medium Term

* Liquidity analysis
* Premium / Discount analysis
* Multi-timeframe confluence
* Historical signal tracking
* Backtesting
* Performance evaluation
* Signal lifecycle/history analysis
* Automated position management

### Long Term

* Production Live trading activation
* Production safety controls
* Notifications
* Monitoring
* Advanced strategy evaluation
* Operational recovery and execution monitoring

### Important Execution Status

The project should currently be understood as:

```text
Analysis Pipeline
        +
MT5 Execution Infrastructure
        +
Validated Demo Open/Close
        ↓
Automatic Live Execution
        ↓
NOT YET CONNECTED
```

The successful Demo execution tests do **not** mean that automatic Live trading is enabled.

---

# 35. Documentation Policy

This repository is intended to be maintainable by a developer who did not originally design it.

Documentation therefore follows these principles:

1. Documentation describes actual behavior.
2. Architecture decisions are documented explicitly.
3. Strategy rules are documented separately from implementation details where necessary.
4. New components must have a clear responsibility.
5. Important changes should update documentation in the same development cycle.
6. The README should remain a reliable map of the project.
7. Detailed technical documentation should be added under `docs/` as the project grows.
8. If code and documentation disagree, the discrepancy must be resolved rather than silently ignored.

---

# 36. Recommended Development Workflow

When implementing a new feature:

```text
1. Understand the existing architecture
        ↓
2. Identify the correct layer
        ↓
3. Define/update the domain model if necessary
        ↓
4. Implement the smallest isolated change
        ↓
5. Add focused tests
        ↓
6. Run the complete test suite
        ↓
7. Update documentation
        ↓
8. Review git diff
        ↓
9. Commit the change
```

When fixing a bug:

```text
1. Reproduce the bug
        ↓
2. Identify the responsible component
        ↓
3. Add/adjust a regression test
        ↓
4. Fix the component
        ↓
5. Run focused tests
        ↓
6. Run all tests
        ↓
7. Update documentation if behavior changed
        ↓
8. Commit
```

---

# 37. Design Philosophy

The project prioritizes:

- Clear responsibilities
- Explicit dependencies
- Small and testable components
- Deterministic analysis
- Incremental development
- Strategy/business logic separated from infrastructure
- Extensibility through discovery and engines
- Documentation alongside implementation
- No silent changes to trading semantics

The architecture should evolve deliberately rather than accumulating shortcuts that make future strategy development harder.

---

# 38. Recommended Development Workflow

When implementing a new feature:

```text
1. Understand the existing architecture
        ↓
2. Identify the correct layer
        ↓
3. Define/update the domain model if necessary
        ↓
4. Implement the smallest isolated change
        ↓
5. Add focused tests
        ↓
6. Run the complete test suite when appropriate
        ↓
7. Update documentation
        ↓
8. Review git diff
        ↓
9. Commit the change
```

For trading-execution changes, Demo-account validation should be performed before considering the corresponding execution path ready for production use.

---

# 39. Execution Safety

The execution layer is designed to separate analysis from broker interaction.

The following distinction is important:

```text
Scanner Signal
    ≠
Trade Plan
    ≠
MT5 Order
```

A scanner signal represents a detected opportunity.

A Trade Plan represents an executable strategy setup after the required entry, stop-loss, and take-profit stages have succeeded.

An MT5 Order represents an explicit broker execution request.

Automatic execution should only occur after the required validation and risk-management stages have completed.

The current project has validated the MT5 execution infrastructure on a Demo account, but automatic execution from the Live pipeline is intentionally not enabled yet.
