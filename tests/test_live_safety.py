"""Tests for live_safety.py risk limits (Phase 4)."""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone

from forex_bot_platform.execution.live_safety import (
    LiveSafety, LiveRiskState, SafetyLevel
)

class TestLiveSafety:
    """Test safety checks for live trading."""
    
    def test_default_limits_are_conservative(self):
        """Default risk limits are conservative."""
        safety = LiveSafety(account_balance=10000)
        limits = safety.get_limits()
        
        # Risk per trade should be 0.25% default
        assert limits["risk_per_trade"] == 0.0025
        # Max should be 0.5%
        assert limits["max_risk_per_trade"] == 0.005
        # Daily loss max 1%
        assert limits["max_daily_loss"] == 100  # 1% of 10000
        # Weekly loss max 3%
        assert limits["max_weekly_loss"] == 300  # 3% of 10000
    
    def test_risk_per_trade_check(self):
        """Check risk per trade limit."""
        safety = LiveSafety(account_balance=10000)
        
        # 0.25% = OK
        assert safety.check_risk_per_trade(0.0025)
        # 0.5% = OK (at limit)
        assert safety.check_risk_per_trade(0.005)
        # 1% = FAIL
        assert not safety.check_risk_per_trade(0.01)
    
    def test_daily_loss_check(self):
        """Check daily loss limit."""
        safety = LiveSafety(account_balance=10000)
        
        # $50 loss = OK
        assert safety.check_daily_loss(-50)
        # $100 loss = OK (at limit)
        assert safety.check_daily_loss(-100)
        # $200 loss = FAIL
        assert not safety.check_daily_loss(-200)
    
    def test_weekly_loss_check(self):
        """Check weekly loss limit."""
        safety = LiveSafety(account_balance=10000)
        
        # $200 loss = OK
        assert safety.check_weekly_loss(-200)
        # $300 loss = OK (at limit)
        assert safety.check_weekly_loss(-300)
        # $500 loss = FAIL
        assert not safety.check_weekly_loss(-500)
    
    def test_drawdown_check(self):
        """Check drawdown limit."""
        safety = LiveSafety(account_balance=10000)
        
        # 3% drawdown = OK
        assert safety.check_drawdown(9700)
        # 5% drawdown = OK (at limit)
        assert safety.check_drawdown(9500)
        # 10% drawdown = FAIL
        assert safety.check_drawdown(9000) is False
    
    def test_max_positions_check(self):
        """Check max positions limit."""
        safety = LiveSafety(account_balance=10000)
        
        # 2 positions = OK (under limit)
        assert safety.check_max_positions(2)
        # 3 positions = FAIL (at max, not less than)
        assert not safety.check_max_positions(3)
        # 4 positions = FAIL (over limit)
        assert not safety.check_max_positions(4)
    
    def test_max_exposure_check(self):
        """Check total exposure limit."""
        safety = LiveSafety(account_balance=10000)
        
        # $8000 = OK
        assert safety.check_max_exposure(8000)
        # $10000 = OK (at limit)
        assert safety.check_max_exposure(10000)
        # $15000 = FAIL
        assert not safety.check_max_exposure(15000)
    
    def test_spread_check(self):
        """Check spread limit."""
        safety = LiveSafety(account_balance=10000)
        
        # 2 pips = OK
        assert safety.check_spread(2.0)
        # 3 pips = OK (at limit)
        assert safety.check_spread(3.0)
        # 5 pips = FAIL
        assert not safety.check_spread(5.0)
    
    def test_slippage_check(self):
        """Check slippage limit."""
        safety = LiveSafety(account_balance=10000)
        
        # 0.0003 = OK
        assert safety.check_slippage(0.0003)
        # 0.0005 = OK (at limit)
        assert safety.check_slippage(0.0005)
        # 0.001 = FAIL
        assert not safety.check_slippage(0.001)
    
    def test_risk_state_to_dict(self):
        """Risk state serializes to dict."""
        state = LiveRiskState(
            daily_pnl=100.0,
            weekly_pnl=200.0,
            total_pnl=300.0,
            positions_today=5,
            max_drawdown=0.03,
        )
        
        data = state.to_dict()
        
        assert data["daily_pnl"] == 100.0
        assert data["weekly_pnl"] == 200.0
        assert data["total_pnl"] == 300.0
        assert data["positions_today"] == 5
    
    def test_risk_state_from_dict(self):
        """Risk state deserializes from dict."""
        data = {
            "daily_pnl": 100.0,
            "weekly_pnl": 200.0,
            "total_pnl": 300.0,
            "positions_today": 5,
            "max_drawdown": 0.03,
            "last_reset": datetime.now(timezone.utc).isoformat(),
        }
        
        state = LiveRiskState.from_dict(data)
        
        assert state.daily_pnl == 100.0
        assert state.weekly_pnl == 200.0
        assert state.positions_today == 5
    
    def test_reset_daily(self):
        """Reset daily tracking."""
        safety = LiveSafety(account_balance=10000)
        safety.risk_state.daily_pnl = -50.0
        safety.risk_state.positions_today = 3
        
        safety.reset_daily()
        
        assert safety.risk_state.daily_pnl == 0.0
        assert safety.risk_state.positions_today == 0
    
    def test_reset_all(self):
        """Reset all tracking."""
        safety = LiveSafety(account_balance=10000)
        safety.risk_state.daily_pnl = -50.0
        safety.risk_state.weekly_pnl = -100.0
        
        safety.reset_all()
        
        assert safety.risk_state.daily_pnl == 0.0
        assert safety.risk_state.weekly_pnl == 0.0
    
    def test_get_safety_report_format(self):
        """Safety report has correct format."""
        safety = LiveSafety(account_balance=10000)
        
        report = safety.get_safety_report()
        
        assert "Live Safety" in report
        assert "Balance" in report
        assert "Risk Limits" in report
    
    def test_hard_max_risk_no_bypass(self):
        """Hard max risk cannot be bypassed."""
        safety = LiveSafety(account_balance=10000)
        
        # Even with magic, cannot exceed hard max
        assert not safety.check_risk_per_trade(0.01)  # 1%
        assert not safety.check_risk_per_trade(0.05)  # 5%
        assert not safety.check_risk_per_trade(0.10)  # 10%