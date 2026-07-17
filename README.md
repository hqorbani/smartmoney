# SmartMoney

Smart Money Concepts (SMC) trading framework for MetaTrader 5.

The project is designed with a modular architecture so new analyzers,
scanners, scoring rules and outputs can be added without changing the
core engine.

---

# Features

## Market Data

- MetaTrader 5 integration
- Multi-symbol scanning
- Multi-timeframe scanning
- Live market monitoring

## Analysis

- Swing Detection
- Fair Value Gap (FVG)
- FVG Lifecycle
    - Active
    - Mitigated
    - Filled
- ICT Order Block

## Scanners

- Active FVG
- Order Block + Active FVG

## Scoring

- Rule-based Signal Scoring

## Outputs

- Console
- CSV
- Signal History

## Visualization

- Candlestick Chart
- Swing Points
- FVG Zones
- Order Blocks

---

# Project Structure

```
apps/
smartmoney/
tests/
outputs/
```

---

# Run Live Scanner

```bash
python -m apps.live
```

---

# Show Chart

```bash
python -m apps.chart
```

---

# Current Architecture

```
MT5
 │
 ▼
Scheduler
 │
 ├─────────────┐
 ▼             ▼
Analyzer     Scanner
 │             │
 └──────┬──────┘
        ▼
    Score Engine
        ▼
   Output Engine
        ▼
 Console / CSV
```

---

# Roadmap

## Completed

- MT5 Provider
- Context Manager
- Swing Analyzer
- FVG Analyzer
- FVG Lifecycle
- Order Block Analyzer
- Active FVG Scanner
- Order Block + Active FVG Scanner
- CSV Output
- Score Engine

## Next

- Bootstrap
- Signal Repository
- Query Engine
- Structure Analyzer
- BOS
- CHOCH
- Liquidity
- Premium / Discount
- Multi-Timeframe Confluence
- Telegram Notifications

---

# License

Private project.