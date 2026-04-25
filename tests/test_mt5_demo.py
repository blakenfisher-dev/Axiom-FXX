import pytest
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from forex_bot_platform.execution.mt5_executor import (
    MT5DemoExecutor, AccountType, OrderSide, SafetyConfig,
    DemoTradingError, LiveAccountBlockedError, SafetyCheckFailedError
)

def test_demo_account_allowed():
    """Test that demo accounts are allowed."""
    config = SafetyConfig(allow_demo_only=True)
    executor = MT5DemoExecutor(login="demo123", password="pass", server="DemoServer", safety_config=config)
    
    # Would connect (mock) - for now test account type detection
    executor._init_mt5()
    assert executor.is_connected
    assert executor.account.account_type == AccountType.DEMO

def test_live_account_blocked():
    """Test that live accounts are blocked."""
    config = SafetyConfig(allow_demo_only=True)
    executor = MT5DemoExecutor(login="live123", password="pass", server="RealServer", safety_config=config)
    
    # Force live account type
    executor._init_mt5()
    executor.account.account_type = AccountType.LIVE
    
    # Should raise on connect
    with pytest.raises(LiveAccountBlockedError):
        executor.connect()

def test_unknown_account_blocked():
    """Test that unknown account types are blocked."""
    config = SafetyConfig(allow_demo_only=True)
    executor = MT5DemoExecutor(login="unknown", password="pass", server="SomeServer", safety_config=config)
    
    # Force unknown account type
    executor._init_mt5()
    executor.account.account_type = AccountType.UNKNOWN
    
    # Should raise on connect
    with pytest.raises(LiveAccountBlockedError):
        executor.connect()

def test_missing_stop_loss_blocked():
    """Test that orders without stop-loss are blocked."""
    config = SafetyConfig(require_stop_loss=True, max_open_trades=3)
    executor = MT5DemoExecutor(login="demo123", password="pass", server="DemoServer", safety_config=config)
    executor._init_mt5()
    executor.is_connected = True
    
    # Should raise - no stop loss
    with pytest.raises(SafetyCheckFailedError, match="Stop-loss required"):
        executor.place_demo_order("EURUSD", OrderSide.BUY, 0.1, stop_loss=None)

def test_high_spread_blocked():
    """Test that high spread orders are blocked."""
    config = SafetyConfig(max_spread=2.0, require_stop_loss=True, max_open_trades=3)
    executor = MT5DemoExecutor(login="demo123", password="pass", server="DemoServer", safety_config=config)
    executor._init_mt5()
    executor.is_connected = True
    
    # Override get_symbol_info to return high spread
    original_get_symbol_info = executor.get_symbol_info
    def mock_symbol_info(symbol):
        return {"symbol": symbol, "spread": 5, "trade_contract_size": 100000}
    executor.get_symbol_info = mock_symbol_info
    
    # Should raise - spread too high
    with pytest.raises(SafetyCheckFailedError, match="Spread too high"):
        executor.place_demo_order("EURUSD", OrderSide.BUY, 0.1, stop_loss=1.0900)

def test_max_open_trades_blocked():
    """Test that max open trades limit is enforced."""
    config = SafetyConfig(require_stop_loss=True, max_open_trades=2)
    executor = MT5DemoExecutor(login="demo123", password="pass", server="DemoServer", safety_config=config)
    executor._init_mt5()
    executor.is_connected = True
    
    # Override get_symbol_info to return low spread
    def mock_symbol_info(symbol):
        return {"symbol": symbol, "spread": 1, "trade_contract_size": 100000}
    executor.get_symbol_info = mock_symbol_info
    
    # Place max trades
    executor.place_demo_order("EURUSD", OrderSide.BUY, 0.1, stop_loss=1.0900)
    executor.place_demo_order("GBPUSD", OrderSide.BUY, 0.1, stop_loss=1.2500)
    
    # Third should be blocked
    with pytest.raises(SafetyCheckFailedError, match="Max open trades"):
        executor.place_demo_order("USDJPY", OrderSide.BUY, 0.1, stop_loss=150.0)

def test_duplicate_order_blocked():
    """Test that duplicate orders are blocked."""
    config = SafetyConfig(require_stop_loss=True, max_open_trades=3)
    executor = MT5DemoExecutor(login="demo123", password="pass", server="DemoServer", safety_config=config)
    executor._init_mt5()
    executor.is_connected = True
    
    # Override get_symbol_info
    def mock_symbol_info(symbol):
        return {"symbol": symbol, "spread": 1, "trade_contract_size": 100000}
    executor.get_symbol_info = mock_symbol_info
    
    # Place first order
    executor.place_demo_order("EURUSD", OrderSide.BUY, 0.1, stop_loss=1.0900)
    
    # Duplicate should be blocked
    with pytest.raises(SafetyCheckFailedError, match="Duplicate"):
        executor.place_demo_order("EURUSD", OrderSide.BUY, 0.1, stop_loss=1.0900)

def test_max_daily_loss_blocked():
    """Test that max daily loss triggers stop."""
    config = SafetyConfig(max_daily_loss=100.0, require_stop_loss=True, max_open_trades=3)
    executor = MT5DemoExecutor(login="demo123", password="pass", server="DemoServer", safety_config=config)
    executor._init_mt5()
    executor.is_connected = True
    executor.daily_stats.realized_pnl = -150.0  # Already over limit
    
    # Should raise - daily loss exceeded
    with pytest.raises(SafetyCheckFailedError, match="Max daily loss"):
        executor.place_demo_order("EURUSD", OrderSide.BUY, 0.1, stop_loss=1.0900)

def test_emergency_stop():
    """Test emergency stop functionality."""
    config = SafetyConfig()
    executor = MT5DemoExecutor(login="demo123", password="pass", server="DemoServer", safety_config=config)
    executor._init_mt5()
    executor.is_connected = True
    
    # Override get_symbol_info
    def mock_symbol_info(symbol):
        return {"symbol": symbol, "spread": 1, "trade_contract_size": 100000}
    executor.get_symbol_info = mock_symbol_info
    
    # Place order
    executor.place_demo_order("EURUSD", OrderSide.BUY, 0.1, stop_loss=1.0900)
    assert len(executor.positions) == 1
    
    # Trigger emergency stop
    reason = executor.emergency_stop()
    assert reason == "emergency_stop_triggered"
    assert len(executor.positions) == 0
    assert executor.daily_stats.emergency_stop_triggered == True

def test_get_safety_status():
    """Test safety status reporting."""
    config = SafetyConfig(max_daily_loss=1000.0, max_open_trades=3)
    executor = MT5DemoExecutor(login="demo123", password="pass", server="DemoServer", safety_config=config)
    executor._init_mt5()
    executor.is_connected = True
    
    status = executor.get_safety_status()
    assert "is_connected" in status
    assert "account_type" in status
    assert "daily_pnl" in status
    assert "max_daily_loss" in status
    assert status["account_type"] == "demo"

def test_get_account_info():
    """Test account info retrieval."""
    config = SafetyConfig()
    executor = MT5DemoExecutor(login="demo123", password="pass", server="DemoServer", safety_config=config)
    executor._init_mt5()
    
    info = executor.get_account_info()
    assert info["login"] == "demo123"
    assert info["server"] == "DemoServer"
    assert info["account_type"] == "demo"

def test_get_positions():
    """Test position listing."""
    config = SafetyConfig(max_daily_loss=1000.0, max_open_trades=3, require_stop_loss=True)
    executor = MT5DemoExecutor(login="demo123", password="pass", server="DemoServer", safety_config=config)
    executor._init_mt5()
    executor.is_connected = True
    
    # Override get_symbol_info
    def mock_symbol_info(symbol):
        return {"symbol": symbol, "spread": 1, "trade_contract_size": 100000}
    executor.get_symbol_info = mock_symbol_info
    
    # Place order
    executor.place_demo_order("EURUSD", OrderSide.BUY, 0.1, stop_loss=1.0900)
    
    positions = executor.get_open_positions()
    assert len(positions) == 1
    assert positions[0]["symbol"] == "EURUSD"