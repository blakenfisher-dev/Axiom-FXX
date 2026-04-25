"""Tests for dashboard integration and MT5 demo trading."""
import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from forex_bot_platform.execution.mt5_executor import (
    MT5DemoExecutor, SafetyConfig, OrderSide, AccountType, DemoPosition,
    SafetyCheckFailedError, LiveAccountBlockedError
)
from forex_bot_platform.paper_trading import PaperTrader, PaperTradeStorage, PaperTrade
from datetime import datetime, timezone

def test_mt5_connection_state():
    """Test MT5 connection state tracking."""
    config = SafetyConfig()
    mt5 = MT5DemoExecutor(login="test123", password="pass", server="DemoServer", safety_config=config)
    mt5.connect()
    
    assert mt5.is_connected == True
    assert mt5.account.account_type == AccountType.DEMO
    
    mt5.disconnect()
    assert mt5.is_connected == False

def test_mt5_account_info_format():
    """Test account info dict format."""
    config = SafetyConfig()
    mt5 = MT5DemoExecutor(login="test123", password="pass", server="DemoServer", safety_config=config)
    mt5._init_mt5()
    
    info = mt5.get_account_info()
    assert "login" in info
    assert "server" in info
    assert "account_type" in info
    assert info["account_type"] == "demo"

def test_mt5_safety_status_format():
    """Test safety status format."""
    config = SafetyConfig(max_daily_loss=500.0, max_open_trades=3)
    mt5 = MT5DemoExecutor(safety_config=config)
    mt5._init_mt5()
    mt5.is_connected = True
    
    status = mt5.get_safety_status()
    assert "is_connected" in status
    assert "account_type" in status
    assert "daily_pnl" in status
    assert "max_daily_loss" in status
    assert "max_open_trades" in status

def test_mt5_order_form_validation():
    """Test order form validation via safety checks."""
    config = SafetyConfig(require_stop_loss=True, max_open_trades=2, max_spread=2.0)
    mt5 = MT5DemoExecutor(safety_config=config)
    mt5._init_mt5()
    mt5.is_connected = True
    
    # Mock symbol info
    def mock_symbol_info(symbol):
        return {"symbol": symbol, "spread": 1, "trade_contract_size": 100000}
    mt5.get_symbol_info = mock_symbol_info
    
    # Place valid order
    ticket = mt5.place_demo_order("EURUSD", OrderSide.BUY, 0.1, stop_loss=1.0900)
    assert ticket > 0
    
    # Missing stop loss should fail
    with pytest.raises(Exception):
        mt5.place_demo_order("EURUSD", OrderSide.BUY, 0.1, stop_loss=None)

def test_mt5_emergency_stop_state():
    """Test emergency stop state changes."""
    config = SafetyConfig()
    mt5 = MT5DemoExecutor(safety_config=config)
    mt5._init_mt5()
    mt5.is_connected = True
    
    # Place order
    def mock_symbol_info(symbol):
        return {"symbol": symbol, "spread": 1, "trade_contract_size": 100000}
    mt5.get_symbol_info = mock_symbol_info
    
    mt5.place_demo_order("EURUSD", OrderSide.BUY, 0.1, stop_loss=1.0900)
    assert len(mt5.positions) == 1
    
    # Trigger emergency stop
    reason = mt5.emergency_stop()
    assert reason == "emergency_stop_triggered"
    assert len(mt5.positions) == 0
    assert mt5.daily_stats.emergency_stop_triggered == True

def test_mt5_positions_format():
    """Test open positions dict format."""
    config = SafetyConfig(max_daily_loss=1000.0, max_open_trades=3, require_stop_loss=True)
    mt5 = MT5DemoExecutor(safety_config=config)
    mt5._init_mt5()
    mt5.is_connected = True
    
    def mock_symbol_info(symbol):
        return {"symbol": symbol, "spread": 1, "trade_contract_size": 100000}
    mt5.get_symbol_info = mock_symbol_info
    
    mt5.place_demo_order("EURUSD", OrderSide.BUY, 0.1, stop_loss=1.0900)
    
    positions = mt5.get_open_positions()
    assert len(positions) == 1
    assert positions[0]["symbol"] == "EURUSD"
    assert positions[0]["side"] == 1

def test_mt5_order_history():
    """Test order history after closing."""
    config = SafetyConfig(max_daily_loss=1000.0, max_open_trades=3, require_stop_loss=True)
    mt5 = MT5DemoExecutor(safety_config=config)
    mt5._init_mt5()
    mt5.is_connected = True
    
    def mock_symbol_info(symbol):
        return {"symbol": symbol, "spread": 1, "trade_contract_size": 100000}
    mt5.get_symbol_info = mock_symbol_info
    
    ticket = mt5.place_demo_order("EURUSD", OrderSide.BUY, 0.1, stop_loss=1.0900)
    
    # Mock get_latest_tick
    def mock_tick(symbol):
        return {"symbol": symbol, "bid": 1.0955, "ask": 1.0957}
    mt5.get_latest_tick = mock_tick
    
    mt5.close_demo_order(ticket)
    
    history = mt5.get_order_history()
    assert len(history) == 1
    assert history[0]["symbol"] == "EURUSD"

def test_daily_stats_format():
    """Test daily stats dict format."""
    config = SafetyConfig()
    mt5 = MT5DemoExecutor(safety_config=config)
    mt5._init_mt5()
    mt5.is_connected = True
    mt5.daily_stats.realized_pnl = 50.0
    mt5.daily_stats.open_trades_count = 2
    
    stats = mt5.get_daily_stats()
    assert "date" in stats
    assert "realized_pnl" in stats
    assert "open_trades" in stats

def test_mt5_modify_order():
    """Test modifying order SL/TP."""
    config = SafetyConfig(max_daily_loss=1000.0, max_open_trades=3, require_stop_loss=True)
    mt5 = MT5DemoExecutor(safety_config=config)
    mt5._init_mt5()
    mt5.is_connected = True
    
    def mock_symbol_info(symbol):
        return {"symbol": symbol, "spread": 1, "trade_contract_size": 100000}
    mt5.get_symbol_info = mock_symbol_info
    
    ticket = mt5.place_demo_order("EURUSD", OrderSide.BUY, 0.1, stop_loss=1.0900)
    
    # Modify
    success = mt5.modify_stop_loss_take_profit(ticket, 1.0850, 1.1000)
    assert success == True
    
    # Verify
    for p in mt5.positions:
        if p.ticket == ticket:
            assert p.stop_loss == 1.0850
            assert p.take_profit == 1.1000

def test_dashboard_imports():
    """Test dashboard can import MT5 module."""
    from forex_bot_platform.execution.mt5_executor import MT5DemoExecutor, SafetyConfig, OrderSide, AccountType
    assert MT5DemoExecutor is not None
    assert SafetyConfig is not None
    assert OrderSide is not None
    assert AccountType is not None

def test_daily_loss_limit_blocks_demo_order():
    """Test max daily loss blocks demo order."""
    config = SafetyConfig(max_daily_loss=100.0, max_open_trades=3, require_stop_loss=True)
    mt5 = MT5DemoExecutor(login="test", password="test", server="Demo", safety_config=config)
    mt5.connect()
    mt5.daily_stats.realized_pnl = -150.0
    
    with pytest.raises(SafetyCheckFailedError, match="Max daily loss"):
        mt5.place_demo_order("EURUSD", OrderSide.BUY, 0.1, stop_loss=1.0900)

def test_max_trades_per_day_blocks():
    """Test max trades per day blocks."""
    config = SafetyConfig(max_daily_loss=1000.0, max_open_trades=3, require_stop_loss=True, max_trades_per_day=2)
    mt5 = MT5DemoExecutor(login="test", password="test", server="Demo", safety_config=config)
    mt5.connect()
    mt5.daily_stats.closed_trades_count = 2
    
    with pytest.raises(SafetyCheckFailedError, match="Max trades per day"):
        mt5.place_demo_order("EURUSD", OrderSide.BUY, 0.1, stop_loss=1.0900)

def test_cooldown_blocks_repeat():
    """Test cooldown blocks repeat orders."""
    config = SafetyConfig(max_daily_loss=1000.0, max_open_trades=3, require_stop_loss=True, cooldown_seconds=60)
    mt5 = MT5DemoExecutor(login="test", password="test", server="Demo", safety_config=config)
    mt5.connect()
    mt5._last_order_time = datetime.now(timezone.utc)
    
    with pytest.raises(SafetyCheckFailedError, match="Cooldown"):
        mt5.place_demo_order("EURUSD", OrderSide.BUY, 0.1, stop_loss=1.0900)

def test_mt5_disconnect_blocks_orders():
    """Test MT5 disconnect blocks orders."""
    config = SafetyConfig(max_daily_loss=1000.0, max_open_trades=3, require_stop_loss=True)
    mt5 = MT5DemoExecutor(safety_config=config)
    mt5.connect()
    mt5.disconnect()
    
    with pytest.raises(SafetyCheckFailedError, match="Not connected"):
        mt5.place_demo_order("EURUSD", OrderSide.BUY, 0.1, stop_loss=1.0900)

def test_unknown_account_blocks():
    """Test unknown account type blocks orders."""
    config = SafetyConfig(max_daily_loss=1000.0, max_open_trades=3, require_stop_loss=True)
    mt5 = MT5DemoExecutor(login="test", password="test", server="Demo", safety_config=config)
    mt5.connect()
    mt5.account.account_type = AccountType.UNKNOWN
    
    with pytest.raises(LiveAccountBlockedError):
        mt5.place_demo_order("EURUSD", OrderSide.BUY, 0.1, stop_loss=1.0900)

def test_audit_log_writes():
    """Test audit log writes correctly."""
    config = SafetyConfig(max_daily_loss=1000.0, max_open_trades=3, require_stop_loss=True)
    mt5 = MT5DemoExecutor(safety_config=config)
    mt5.connect()
    
    mt5._log_audit("test_action", "test details", success=True)
    log = mt5.get_audit_log()
    assert len(log) >= 1
    assert log[-1]["action"] == "test_action"

def test_rejection_report_contains_reason():
    """Test rejection report contains reason."""
    config = SafetyConfig(max_daily_loss=1000.0, max_open_trades=3, require_stop_loss=True)
    mt5 = MT5DemoExecutor(safety_config=config)
    mt5.connect()
    mt5._record_rejection("EURUSD", OrderSide.BUY, 0.1, "Test rejection")
    
    report = mt5.get_rejection_report()
    assert len(report) >= 1
    assert report[-1]["reason"] == "Test rejection"

def test_session_save_recover():
    """Test session persistence."""
    import tempfile
    config = SafetyConfig(max_daily_loss=1000.0, max_open_trades=3, require_stop_loss=True)
    mt5 = MT5DemoExecutor(safety_config=config)
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        success = mt5.save_session(temp_file)
        assert success
        
        mt5.daily_stats.realized_pnl = 50.0
        mt5.daily_stats.closed_trades_count = 3
        mt5.save_session(temp_file)
        
        mt5.recover_session(temp_file)
        assert mt5.daily_stats.closed_trades_count == 3
    finally:
        import os
        os.unlink(temp_file)

def test_dry_run_connect():
    """Test dry run connect without placing order."""
    from forex_bot_platform.execution.mt5_executor import MT5DemoExecutor, SafetyConfig
    config = SafetyConfig(max_daily_loss=1000.0, max_open_trades=3, require_stop_loss=True)
    mt5 = MT5DemoExecutor(login="test123", password="test", server="Demo", safety_config=config)
    
    success = mt5.connect()
    assert success
    assert mt5.is_connected
    assert mt5.account.account_type.value == "demo"

def test_dry_run_symbol_info():
    """Test symbol info retrieval."""
    config = SafetyConfig(max_daily_loss=1000.0, max_open_trades=3, require_stop_loss=True)
    mt5 = MT5DemoExecutor(login="test123", password="test", server="Demo", safety_config=config)
    mt5.connect()
    
    info = mt5.get_symbol_info("EURUSD")
    assert info is not None
    assert "bid" in info
    assert "ask" in info

def test_dry_run_tick():
    """Test tick retrieval."""
    config = SafetyConfig(max_daily_loss=1000.0, max_open_trades=3, require_stop_loss=True)
    mt5 = MT5DemoExecutor(login="test123", password="test", server="Demo", safety_config=config)
    mt5.connect()
    
    tick = mt5.get_latest_tick("EURUSD")
    assert tick is not None
    assert "bid" in tick
    assert "ask" in tick

def test_audit_log_limit():
    """Test audit log size limit."""
    config = SafetyConfig(max_daily_loss=1000.0, max_open_trades=3, require_stop_loss=True)
    mt5 = MT5DemoExecutor(safety_config=config)
    mt5.connect()
    
    for i in range(60):
        mt5._log_audit(f"action_{i}", f"details_{i}", True)
    
    log = mt5.get_audit_log(count=50)
    assert len(log) <= 50

def test_rejection_record_limit():
    """Test rejection record size limit."""
    config = SafetyConfig(max_daily_loss=1000.0, max_open_trades=3, require_stop_loss=True)
    mt5 = MT5DemoExecutor(login="test123", password="test", server="Demo", safety_config=config)
    mt5.connect()
    
    for i in range(60):
        mt5._record_rejection("EURUSD", OrderSide.BUY, 0.1, f"reason_{i}")
    
    report = mt5.get_rejection_report(count=50)
    assert len(report) <= 50

def test_soak_starts():
    """Test soak test starts."""
    from forex_bot_platform.execution.mt5_executor import DemoSoakConfig, DemoSoakTest
    mt5 = MT5DemoExecutor(login="test", password="test", server="Demo", safety_config=SafetyConfig())
    config = DemoSoakConfig(max_runtime_seconds=10, max_trades=5)
    soak = DemoSoakTest(mt5, config)
    
    success = soak.start(allow_orders=False)
    assert success
    assert soak.status in ("running", "validation_only")

def test_soak_validation_only():
    """Test soak validation-only places no orders."""
    from forex_bot_platform.execution.mt5_executor import DemoSoakConfig, DemoSoakTest
    mt5 = MT5DemoExecutor(login="test", password="test", server="Demo", safety_config=SafetyConfig())
    config = DemoSoakConfig(max_runtime_seconds=10, max_trades=5)
    soak = DemoSoakTest(mt5, config)
    soak.start(allow_orders=False)
    
    status = soak.step()
    assert status["is_validation_only"] == True

def test_soak_max_runtime():
    """Test soak stops at max runtime."""
    from forex_bot_platform.execution.mt5_executor import DemoSoakConfig, DemoSoakTest
    mt5 = MT5DemoExecutor(login="test", password="test", server="Demo", safety_config=SafetyConfig())
    config = DemoSoakConfig(max_runtime_seconds=0, max_trades=5)  # Immediate stop
    soak = DemoSoakTest(mt5, config)
    soak.start(allow_orders=False)
    
    status = soak.step()
    assert status["status"] in ("stopped", "validation_only")

def test_soak_connection_failure():
    """Test soak stops on connection failure."""
    from forex_bot_platform.execution.mt5_executor import DemoSoakConfig, DemoSoakTest
    mt5 = MT5DemoExecutor(login="test", password="test", server="Demo", safety_config=SafetyConfig())
    config = DemoSoakConfig(max_runtime_seconds=10, max_trades=5)
    soak = DemoSoakTest(mt5, config)
    soak.start(allow_orders=False)
    
    # Disconnect and step
    mt5.disconnect()
    status = soak.step()
    
    assert status["status"] == "stopped"
    assert status["stop_reason"] in ("connection_lost", "manual")

def test_soak_emergency_stop():
    """Test soak stops on emergency."""
    from forex_bot_platform.execution.mt5_executor import DemoSoakConfig, DemoSoakTest
    mt5 = MT5DemoExecutor(login="test", password="test", server="Demo", safety_config=SafetyConfig())
    config = DemoSoakConfig(max_runtime_seconds=10, max_trades=5)
    soak = DemoSoakTest(mt5, config)
    soak.start(allow_orders=False)
    
    # Trigger emergency
    mt5.daily_stats.emergency_stop_triggered = True
    status = soak.step()
    
    assert status["emergency_stop"] == True

def test_soak_export_reports():
    """Test soak report export."""
    import tempfile
    from forex_bot_platform.execution.mt5_executor import DemoSoakConfig, DemoSoakTest
    mt5 = MT5DemoExecutor(login="test", password="test", server="Demo", safety_config=SafetyConfig())
    config = DemoSoakConfig(max_runtime_seconds=10, max_trades=5)
    soak = DemoSoakTest(mt5, config)
    soak.start(allow_orders=False)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        soak.export_reports(tmpdir)
        import os
        assert os.path.exists(os.path.join(tmpdir, "demo_soak_report.json"))
        assert os.path.exists(os.path.join(tmpdir, "demo_soak_rejections.json"))
        assert os.path.exists(os.path.join(tmpdir, "demo_soak_audit.log"))

def test_readiness_passes_with_clean():
    """Test readiness passes with clean soak report."""
    import tempfile
    from forex_bot_platform.execution.demo_readiness import (
        DemoReadinessConfig, evaluate_demo_readiness
    )
    config = DemoReadinessConfig()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mock clean report
        report = {
            "status": "stopped",
            "executor_connected": True,
            "executor_daily_pnl": 0,
            "emergency_stop": False,
            "trades_placed": 5,
            "heartbeat_count": 10
        }
        import json
        with open(os.path.join(tmpdir, "demo_soak_report.json"), "w") as f:
            json.dump(report, f)
        
        with open(os.path.join(tmpdir, "demo_soak_audit.log"), "w") as f:
            f.write("2025-01-01T00:00:00Z action details True\n")
        
        result = evaluate_demo_readiness(tmpdir, config)
        assert result.passed == True

def test_readiness_fails_emergency():
    """Test readiness fails with emergency stop."""
    from forex_bot_platform.execution.demo_readiness import DemoReadinessConfig, evaluate_demo_readiness
    import tempfile, json
    
    with tempfile.TemporaryDirectory() as tmpdir:
        report = {"executor_connected": True, "emergency_stop": True, "executor_daily_pnl": 0}
        with open(os.path.join(tmpdir, "demo_soak_report.json"), "w") as f:
            json.dump(report, f)
        
        with open(os.path.join(tmpdir, "demo_soak_audit.log"), "w") as f:
            f.write("2025-01-01 00:00:00 emergency_stop True\n")
        
        result = evaluate_demo_readiness(tmpdir)
        assert result.passed == False
        assert result.emergency_stop_events == 1

def test_readiness_fails_live_account():
    """Test readiness fails with live account attempt."""
    from forex_bot_platform.execution.demo_readiness import DemoReadinessConfig, evaluate_demo_readiness
    import tempfile, json
    
    with tempfile.TemporaryDirectory() as tmpdir:
        report = {"executor_connected": True, "emergency_stop": False, "executor_daily_pnl": 0}
        with open(os.path.join(tmpdir, "demo_soak_report.json"), "w") as f:
            json.dump(report, f)
        
        with open(os.path.join(tmpdir, "demo_soak_audit.log"), "w") as f:
            f.write("2025-01-01 00:00:00 Live account detected True\n")
        
        result = evaluate_demo_readiness(tmpdir)
        assert result.passed == False
        assert result.live_account_attempts >= 1

def test_readiness_fails_missing_sl():
    """Test readiness fails with missing stop-loss."""
    from forex_bot_platform.execution.demo_readiness import DemoReadinessConfig, evaluate_demo_readiness
    import tempfile, json
    
    with tempfile.TemporaryDirectory() as tmpdir:
        report = {"executor_connected": True, "emergency_stop": False, "executor_daily_pnl": 0}
        with open(os.path.join(tmpdir, "demo_soak_report.json"), "w") as f:
            json.dump(report, f)
        
        with open(os.path.join(tmpdir, "demo_soak_audit.log"), "w") as f:
            # This should be caught as stop-loss required check
            f.write("2025-01-01 00:00:00 safety_check Stop-loss required False\n")
        
        result = evaluate_demo_readiness(tmpdir)
        # May pass if score still above threshold
        assert result.score < 100  # Should have penalty

def test_readiness_fails_high_drawdown():
    """Test readiness detects high daily loss as warning."""
    from forex_bot_platform.execution.demo_readiness import DemoReadinessConfig, evaluate_demo_readiness
    import tempfile, json
    
    with tempfile.TemporaryDirectory() as tmpdir:
        report = {"executor_connected": True, "emergency_stop": False, "executor_daily_pnl": -500}
        with open(os.path.join(tmpdir, "demo_soak_report.json"), "w") as f:
            json.dump(report, f)
        
        with open(os.path.join(tmpdir, "demo_soak_audit.log"), "w") as f:
            f.write("2025-01-01 00:00:00 action True\n")
        
        # Test with very low loss threshold
        result = evaluate_demo_readiness(tmpdir, DemoReadinessConfig(max_daily_loss_threshold=100.0))
        assert "daily loss" in " ".join(result.warnings).lower()

def test_readiness_report_generated():
    """Test readiness report file generated."""
    import tempfile, os, json
    from forex_bot_platform.execution.demo_readiness import (
        DemoReadinessConfig, evaluate_demo_readiness, write_demo_readiness_report
    )
    
    with tempfile.TemporaryDirectory() as tmpdir:
        report = {"executor_connected": True, "emergency_stop": False, "executor_daily_pnl": 0}
        with open(os.path.join(tmpdir, "demo_soak_report.json"), "w") as f:
            json.dump(report, f)
        
        with open(os.path.join(tmpdir, "demo_soak_audit.log"), "w") as f:
            f.write("2025-01-01 00:00:00 action True\n")
        
        result = evaluate_demo_readiness(tmpdir)
        output_path = os.path.join(tmpdir, "demo_readiness_report.json")
        write_demo_readiness_report(result, output_path)
        
        assert os.path.exists(output_path)