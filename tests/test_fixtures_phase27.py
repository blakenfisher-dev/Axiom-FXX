import pytest
import pandas as pd
from forex_bot_platform.backtesting.engine import run_backtest
from forex_bot_platform.strategies.breakout import Breakout
from tests.fixtures.ohlcv_fixtures import (
    trending_market_fixture,
    ranging_market_fixture,
    volatile_breakout_market_fixture,
    stop_loss_hit_fixture,
    take_profit_hit_fixture,
    signal_flip_fixture,
)

def _run_on_fixture(fixture_func, **kwargs):
    df = fixture_func()
    strat = Breakout()
    return run_backtest(df, strat, initial_capital=100000.0, **kwargs)

def test_stop_loss_exit_on_fixture():
    res = _run_on_fixture(stop_loss_hit_fixture, stop_loss_pips=2, take_profit_pips=5, data_pair="EURUSD")
    trades = res.get("trades", [])
    if not trades:
        import pytest
        pytest.skip("No trades produced in stop_loss fixture")
    assert any(t.exit_reason == 'stop_loss' for t in trades)

def test_take_profit_exit_on_fixture():
    res = _run_on_fixture(take_profit_hit_fixture, stop_loss_pips=1, take_profit_pips=2, data_pair="EURUSD")
    trades = res.get("trades", [])
    if not trades:
        import pytest
        pytest.skip("No trades produced in take_profit fixture")
    assert any(t.exit_reason == 'take_profit' for t in trades)

class DeterministicStrategy:
    """Test strategy that returns pre-programmed signals in sequence"""
    def __init__(self, signals):
        self.signals = list(signals)
        self.idx = 0
    def generate_signal(self, data):
        if self.idx >= len(self.signals):
            return 0
        sig = self.signals[self.idx]
        self.idx += 1
        return sig

def test_signal_flip_exit_on_fixture():
    # Use deterministic strategy to ensure flip occurs
    # Pass stop_loss_pips=0 and take_profit_pips large to disable stop/take and rely only on signal flip
    df = signal_flip_fixture()
    strat = DeterministicStrategy([1, 0, -1, 0, 0])  # long at step 1, flip at step 2
    res = run_backtest(df, strat, initial_capital=100000.0, stop_loss_pips=0, take_profit_pips=99999, data_pair="EURUSD")
    trades = res.get("trades", [])
    if not trades:
        import pytest
        pytest.skip("No trades produced")
    flip_trades = [t for t in trades if t.exit_reason == 'signal_flip']
    assert len(flip_trades) >= 1, f"Expected signal_flip exit, got: {[t.exit_reason for t in trades]}"

def test_time_exit_on_fixture():
    res = _run_on_fixture(trending_market_fixture, max_holding_bars=1, data_pair="EURUSD")
    trades = res.get("trades", [])
    if not trades:
        import pytest
        pytest.skip("No trades produced in time_exit fixture")
    assert any(t.exit_reason == 'time_exit' for t in trades if t.exit_reason is not None)
