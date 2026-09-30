# SmartMoney

Smart Money Concepts (SMC) market-analysis framework for MetaTrader 5.

SmartMoney is a modular Python project for market-structure analysis, Fair Value Gap (FVG) detection, Order Block detection, signal generation, trade-plan calculation, risk management, visualization, and MetaTrader 5 execution infrastructure.

> **Current status:** The main pipeline is an analysis and signal-generation system. MT5 Demo execution infrastructure exists and has been validated separately. Automatic Live order execution is not connected to the main scanner pipeline.

---

## 1. Features

### Market Analysis

* MetaTrader 5 market-data integration
* Multi-symbol analysis
* Multi-timeframe analysis
* Swing detection and relationships
* Market-structure analysis
* Fair Value Gap detection and lifecycle management
* Order Block detection
* Structure events
* Active-FVG scanning
* Order Block + Active-FVG scanning

### Trade Planning

* Entry validation
* Entry-zone tracking
* Stop-loss calculation
* Take-profit calculation
* Risk/reward calculation
* Generic position-size planning
* Broker-aware MT5 volume calculation

### Execution Infrastructure

* MT5 order-request construction
* MT5 order validation
* MT5 market-order execution
* Demo position opening and closing
* Broker result handling

Execution remains separate from the automatic Live analysis pipeline.

---

## 2. Architecture

The main runtime pipeline is:

```text
MetaTrader 5
     │
     ▼
MT5 Data Provider
     │
     ▼
Scheduler / Signal Scanner
     │
     ▼
MarketContext
     │
     ├── Swing Analysis
     ├── FVG Analysis
     ├── Order Block Analysis
     └── Market Structure
     │
     ▼
Structure Events
     │
     ▼
Scanners
     │
     ▼
Signals
     │
     ▼
Entry / SL / TP
     │
     ▼
Trade Plan
     │
     ▼
Position Size
     │
     ▼
Output / Storage
```

The application composition root is:

```text
smartmoney/bootstrap.py
```

Core orchestration is implemented under:

```text
smartmoney/core/
```

---

## 3. Runtime Flow

For each configured symbol and timeframe, the analysis pipeline:

1. Connects to MetaTrader 5.
2. Retrieves historical market data.
3. Builds or updates `MarketContext`.
4. Updates the current bid/ask from the live MT5 tick.
5. Runs analyzers.
6. Updates market structure and structure events.
7. Runs scanners.
8. Processes generated signals.
9. Builds downstream trade plans when entry conditions are satisfied.
10. Calculates position-size information.
11. Publishes or stores the resulting signals.

The main live-analysis entry point is:

```powershell
python -m apps.live
```

---

## 4. MarketContext

`MarketContext` is the shared state object for one symbol/timeframe analysis cycle.

It contains the market data and intermediate analysis results used by the pipeline, including:

* market data
* swings
* structures
* FVGs
* Order Blocks
* market structure
* swing relationships
* signals
* trade-plan information

Shared analysis state should normally pass through `MarketContext` rather than creating unnecessary direct dependencies between analyzers.

---

## 5. Scanners

Scanners identify candidate opportunities from an analyzed `MarketContext`.

### Active FVG

```text
smartmoney/scanners/active_fvg.py
```

Finds FVGs whose lifecycle status is active.

### Order Block + Active FVG

```text
smartmoney/scanners/orderblock_active_fvg.py
```

Finds Order Blocks associated with active FVGs.

A scanner signal represents an identified opportunity. It does not automatically represent an executable trade.

---

## 6. FVG Lifecycle

FVGs have a lifecycle rather than remaining permanently actionable.

Relevant states include:

```text
ACTIVE
MITIGATED
FILLED
```

Components:

```text
smartmoney/analyzers/fvg.py
smartmoney/analyzers/fvg_lifecycle.py
smartmoney/models/fvg.py
```

Scanners that require an active FVG must check its lifecycle status.

---

## 7. Order Blocks

Order Blocks are detected from the analyzed market structure and FVG relationships.

Relevant components include:

```text
smartmoney/analyzers/orderblock.py
smartmoney/models/orderblock.py
```

Order Blocks can also maintain entry-zone state so that the system can distinguish a first touch from continued presence inside the same zone.

---

## 8. Entry Zones

The current entry model divides an Order Block into three equal zones.

The direction determines the order in which the zones are entered.

### BUY

Price enters the Order Block from the top:

```text
┌─────────────────────┐
│ INITIAL             │
├─────────────────────┤
│ MIDDLE              │
├─────────────────────┤
│ FINAL               │
└─────────────────────┘
```

Definitions:

```text
INITIAL = upper third
MIDDLE  = middle third
FINAL   = lower third
```

For an Order Block with:

```text
ob_low  = L
ob_high = H
zone_size = (H - L) / 3
```

the zones are:

```text
INITIAL = [H - zone_size, H]
MIDDLE  = [H - 2*zone_size, H - zone_size]
FINAL   = [L, H - 2*zone_size]
```

### SELL

Price enters the Order Block from the bottom:

```text
┌─────────────────────┐
│ FINAL               │
├─────────────────────┤
│ MIDDLE              │
├─────────────────────┤
│ INITIAL             │
└─────────────────────┘
```

Definitions:

```text
INITIAL = lower third
MIDDLE  = middle third
FINAL   = upper third
```

The zones are:

```text
INITIAL = [L, L + zone_size]
MIDDLE  = [L + zone_size, L + 2*zone_size]
FINAL   = [L + 2*zone_size, H]
```

The system tracks the `INITIAL` and `MIDDLE` zone state so that the same zone does not repeatedly generate a first-entry event while price remains inside it.

---

## 9. Entry Activation

A detected setup is not automatically an entry.

The conceptual flow is:

```text
Active FVG + Order Block
          │
          ▼
     Scanner Signal
          │
          ▼
 Price reaches Order Block
          │
          ▼
    Entry activation
          │
          ▼
      Stop Loss
          │
          ▼
      Take Profit
          │
          ▼
      Trade Plan
          │
          ▼
     Position Size
```

Therefore:

```text
Scanner Signal
      ≠
Trade Plan
      ≠
MT5 Order
```

An active setup may exist without an active trade plan.

---

## 10. Stop Loss and Take Profit

Stop-loss planning is based on the Order Block boundaries.

For BUY:

```text
SL = Order Block Low
```

For SELL:

```text
SL = Order Block High
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

Configuration is located in:

```text
smartmoney/config.py
```

---

## 11. Position Sizing

Generic position sizing remains broker-independent.

Conceptually:

```text
Account Balance
       │
       ▼
   Risk %
       │
       ▼
 Risk Amount
       │
       ▼
 Stop Distance
       │
       ▼
Position Size Plan
```

The MT5 execution layer then converts the generic risk information into a broker-compatible volume using instrument-specific information such as:

* tick value
* tick size
* volume step
* minimum volume
* maximum volume

---

## 12. MetaTrader 5 Execution

Execution components are located under:

```text
smartmoney/trading/
```

The execution flow is:

```text
Trade Plan
    │
    ▼
Broker-aware Volume
    │
    ▼
MT5 Order Request
    │
    ▼
Order Check
    │
    ▼
Order Send
    │
    ▼
Broker Result
```

Demo execution has been validated for opening and closing positions.

### Important

The successful Demo execution path does **not** mean automatic Live trading is enabled.

The main Live scanner currently generates analysis and signals without automatically submitting broker orders.

---

## 13. Application Entry Points

### Live Scanner

```powershell
python -m apps.live
```

Runs the analysis pipeline against MetaTrader 5.

### Chart

```powershell
python -m apps.chart
```

Runs the visualization application.

### Demo Order

```powershell
python -m apps.demo_order
```

Provides a controlled entry point for MT5 Demo execution testing.

---

## 14. Configuration

Main runtime configuration:

```text
smartmoney/config.py
smartmoney/symbol_config.py
```

Configuration covers areas such as:

* symbols
* timeframes
* historical candle count
* scan interval
* risk percentage
* risk/reward ratio
* signal limits
* scoring configuration
* instrument-specific settings

The current scanner configuration uses short M1-M6 timeframes.

Instrument-specific settings are maintained separately in `symbol_config.py`.

---

## 15. Project Structure

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
│   ├── config.py
│   └── symbol_config.py
│
├── tests/
│
├── tools/
│   └── diagnose_context_state.py
│
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## 16. Important Components

| Area             | Responsibility                                 |
| ---------------- | ---------------------------------------------- |
| `apps/`          | Application entry points                       |
| `core/`          | Orchestration, engines, context and scheduling |
| `models/`        | Domain models                                  |
| `analyzers/`     | Market analysis and trade-plan calculations    |
| `scanners/`      | Opportunity detection                          |
| `scoring/`       | Signal scoring                                 |
| `services/`      | Reusable services                              |
| `repository/`    | Signal storage                                 |
| `query/`         | Signal filtering and sorting                   |
| `trading/`       | Broker and execution infrastructure            |
| `visualization/` | Chart presentation                             |
| `tests/`         | Behavioral verification                        |
| `tools/`         | Diagnostic and development utilities           |

---

## 17. Diagnostic Tools

The repository includes:

```text
tools/diagnose_context_state.py
```

This tool is intended for historical investigation of persistent `MarketContext`, FVG, and Order Block behavior.

It uses the same context and analyzer pipeline as the live scanner while inspecting a selected historical window.

It is a diagnostic tool, not part of the normal Live execution path.

---

## 18. Testing

The project uses `pytest`.

Run the full test suite with:

```powershell
pytest -q
```

For focused tests:

```powershell
pytest -q tests/<test_file>.py
```

For a basic source compilation check:

```powershell
python -m compileall smartmoney
```

Before committing changes:

```powershell
git diff
git diff --cached
git diff --check
```

Strategy or behavior changes should include focused regression tests whenever practical.

---

## 19. Development Rules

The project follows these principles:

1. Keep responsibilities separated between layers.
2. Use `MarketContext` for shared analysis state.
3. Respect analyzer dependencies and execution order.
4. Keep domain models independent.
5. Add regression tests for behavior changes.
6. Do not silently change trading semantics.
7. Keep broker-specific logic inside the execution layer.
8. Update documentation when architecture or strategy semantics change.
9. Prefer small, isolated changes.
10. Review the complete diff before committing.

---

## 20. Execution Safety

The system deliberately separates:

```text
Scanner Signal
      ≠
Trade Plan
      ≠
MT5 Order
```

A scanner signal is an analytical opportunity.

A Trade Plan is a calculated setup containing entry, stop loss, take profit, and risk information.

An MT5 Order is an explicit broker execution request.

Automatic Live execution must not be assumed merely because the execution infrastructure exists or because a Demo order has been successfully tested.

---

## 21. Current Status

The project currently provides:

```text
Market Analysis
      +
Signal Generation
      +
Trade Planning
      +
Risk / Position Sizing
      +
MT5 Execution Infrastructure
      +
Validated Demo Execution
```

The following remain separate development areas:

* automatic Live execution integration
* position lifecycle management
* duplicate-position protection
* advanced execution safeguards
* deeper multi-timeframe strategy development
* historical performance evaluation
* production monitoring and recovery

---

## 22. Development Workflow

For a new feature:

```text
Understand existing architecture
          ↓
Identify the correct layer
          ↓
Implement the smallest isolated change
          ↓
Add focused tests
          ↓
Run tests
          ↓
Review git diff
          ↓
Commit
          ↓
Push
```

For a bug:

```text
Reproduce
   ↓
Identify responsible component
   ↓
Add / adjust regression test
   ↓
Fix
   ↓
Run focused tests
   ↓
Run broader tests
   ↓
Review diff
   ↓
Commit
```

Trading-execution changes should be validated on Demo before being considered for any production integration.

---

## 23. Design Principles

SmartMoney prioritizes:

* clear responsibilities
* explicit dependencies
* small and testable components
* deterministic analysis
* incremental development
* separation of strategy and infrastructure
* extensibility through engines and discovery
* explicit trading semantics
* documentation that describes actual behavior

The README should remain a concise map of the current system. Detailed implementation notes should live closer to the relevant component or under dedicated documentation as the project grows.
