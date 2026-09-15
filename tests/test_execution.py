
from smartmoney.trading.trade_plan import (
    TradeDirection,
    TradePlan,
)

from smartmoney.trading.execution import (
    DryRunExecutor,
    ExecutionResult,
    ExecutionStatus,
)
from smartmoney.trading.execution import (
    DryRunExecutor,
    ExecutionResult,
    ExecutionStatus,
    TradeExecutor,
)

def test_execution_result_can_represent_rejected_trade():
    plan = TradePlan(
        symbol="NAS100",
        timeframe=1,
        direction=TradeDirection.BUY,
        entry_price=29442.3,
        stop_loss=29440.0,
        take_profit=29446.9,
        risk_distance=2.3,
        orderblock_index=21,
    )

    result = ExecutionResult(
        status=ExecutionStatus.REJECTED,
        plan=plan,
        message="Trade rejected",
    )

    assert result.status == ExecutionStatus.REJECTED
    assert result.plan == plan
    assert result.message == "Trade rejected"

def test_dry_run_executor_rejects_zero_risk():
    plan = TradePlan(
        symbol="NAS100",
        timeframe=1,
        direction=TradeDirection.BUY,
        entry_price=29442.3,
        stop_loss=29442.3,
        take_profit=29442.3,
        risk_distance=0.0,
        orderblock_index=21,
    )

    executor = DryRunExecutor()

    result = executor.execute(plan)

    assert result.status == ExecutionStatus.REJECTED
    assert result.plan == plan
    assert result.message == "Trade plan risk must be positive"

def test_dry_run_executor_implements_trade_executor():
    executor = DryRunExecutor()

    assert isinstance(executor, TradeExecutor)

def test_execution_result_stores_dry_run_result():
    plan = TradePlan(
        symbol="NAS100",
        timeframe=1,
        direction=TradeDirection.BUY,
        entry_price=29442.3,
        stop_loss=29440.0,
        take_profit=29446.9,
        risk_distance=2.3,
        orderblock_index=21,
    )

    result = ExecutionResult(
        status=ExecutionStatus.DRY_RUN,
        plan=plan,
        message="Dry-run order accepted",
    )

    assert result.status == ExecutionStatus.DRY_RUN
    assert result.plan == plan
    assert result.message == "Dry-run order accepted"


def test_execution_status_values():
    assert ExecutionStatus.DRY_RUN.value == "dry_run"
    assert ExecutionStatus.EXECUTED.value == "executed"
    assert ExecutionStatus.REJECTED.value == "rejected"

def test_dry_run_executor_does_not_execute_real_order():
    plan = TradePlan(
        symbol="NAS100",
        timeframe=1,
        direction=TradeDirection.BUY,
        entry_price=29442.3,
        stop_loss=29440.0,
        take_profit=29446.9,
        risk_distance=2.3,
        orderblock_index=21,
    )
    executor = DryRunExecutor()

    result = executor.execute(plan)

    assert result.status == ExecutionStatus.DRY_RUN
    assert result.plan == plan
    assert result.message == "Dry-run order accepted"    

def test_dry_run_executor_rejects_invalid_buy_levels():
    plan = TradePlan(
        symbol="NAS100",
        timeframe=1,
        direction=TradeDirection.BUY,
        entry_price=29442.3,
        stop_loss=29445.0,
        take_profit=29440.0,
        risk_distance=2.3,
        orderblock_index=21,
    )

    executor = DryRunExecutor()

    result = executor.execute(plan)

    assert result.status == ExecutionStatus.REJECTED
    assert result.plan == plan
    assert result.message == "Invalid BUY trade levels"

def test_dry_run_executor_rejects_invalid_sell_levels():
    plan = TradePlan(
        symbol="NAS100",
        timeframe=1,
        direction=TradeDirection.SELL,
        entry_price=29427.0,
        stop_loss=29420.0,
        take_profit=29430.0,
        risk_distance=7.0,
        orderblock_index=31,
    )

    executor = DryRunExecutor()

    result = executor.execute(plan)

    assert result.status == ExecutionStatus.REJECTED
    assert result.plan == plan
    assert result.message == "Invalid SELL trade levels"        