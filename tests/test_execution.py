from smartmoney.models.position_size import PositionSizePlan
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

def test_execution_result_can_store_position_size_plan():
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

    position_size_plan = PositionSizePlan(
        balance=10000.0,
        risk_percent=1.0,
        risk_amount=100.0,
        stop_distance=2.3,
        position_size=43.47826087,
    )

    result = ExecutionResult(
        status=ExecutionStatus.DRY_RUN,
        plan=plan,
        message="Dry-run order accepted",
        position_size_plan=position_size_plan,
    )

    assert result.position_size_plan == position_size_plan    

def test_dry_run_executor_stores_position_size_plan():
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

    position_size_plan = PositionSizePlan(
        balance=10000.0,
        risk_percent=1.0,
        risk_amount=100.0,
        stop_distance=2.3,
        position_size=43.47826087,
    )

    executor = DryRunExecutor(
        position_size_plan=position_size_plan,
    )

    result = executor.execute(plan)

    assert result.status == ExecutionStatus.DRY_RUN
    assert result.plan == plan
    assert result.position_size_plan == position_size_plan

def test_dry_run_executor_rejects_non_positive_position_size():
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

    position_size_plan = PositionSizePlan(
        balance=10000.0,
        risk_percent=1.0,
        risk_amount=100.0,
        stop_distance=2.3,
        position_size=0.0,
    )

    executor = DryRunExecutor(
        position_size_plan=position_size_plan,
    )

    result = executor.execute(plan)

    assert result.status == ExecutionStatus.REJECTED
    assert result.plan == plan
    assert result.position_size_plan == position_size_plan
    assert result.message == "Position size must be positive"

def test_dry_run_executor_accepts_plan_without_position_size():
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
    assert result.position_size_plan is None
    assert result.message == "Dry-run order accepted"

def test_dry_run_executor_rejects_non_positive_risk_amount():
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

    position_size_plan = PositionSizePlan(
        balance=10000.0,
        risk_percent=1.0,
        risk_amount=0.0,
        stop_distance=2.3,
        position_size=43.47826087,
    )

    executor = DryRunExecutor(
        position_size_plan=position_size_plan,
    )

    result = executor.execute(plan)

    assert result.status == ExecutionStatus.REJECTED
    assert result.plan == plan
    assert result.position_size_plan == position_size_plan
    assert result.message == "Risk amount must be positive"

def test_dry_run_executor_rejects_non_positive_stop_distance():
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

    position_size_plan = PositionSizePlan(
        balance=10000.0,
        risk_percent=1.0,
        risk_amount=100.0,
        stop_distance=0.0,
        position_size=43.47826087,
    )

    executor = DryRunExecutor(
        position_size_plan=position_size_plan,
    )

    result = executor.execute(plan)

    assert result.status == ExecutionStatus.REJECTED
    assert result.plan == plan
    assert result.position_size_plan == position_size_plan
    assert result.message == "Stop distance must be positive"
        
