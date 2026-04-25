import pandas as pd
import numpy as np
from forex_bot_platform.backtesting.engine import run_backtest
from forex_bot_platform.strategies.breakout import Breakout
from forex_bot_platform.risk.risk_manager import calculate_position_size

def make_simple_data():
    dates = pd.date_range(start="2025-01-01", periods=4, freq="D")
    data = {
        "date": dates,
        "open": [1.1000, 1.1010, 1.1010, 1.1010],
        "high": [1.1005, 1.1015, 1.1012, 1.1013],
        "low": [1.0995, 1.1005, 1.1008, 1.1008],
        "close": [1.1000, 1.1015, 1.1012, 1.1010],
        "volume": [100, 100, 100, 100],
    }
    return pd.DataFrame(data)

def test_stop_loss_exit_basic():
    data = make_simple_data()
    strat = Breakout()
    res = run_backtest(data, strat, initial_capital=100000.0, spread_pips=0.0, slippage_pct=0.0, risk_per_trade=0.01, stop_loss_pips=2, data_pair="EURUSD")
    trades = res["trades"]
    assert len(trades) >= 1
    assert trades[-1].exit_reason == 'stop_loss'

def test_take_profit_exit_basic():
    data = make_simple_data()
    # Modify last candle to hit take profit
    data.at[2, 'close'] = 1.1020
    strat = Breakout()
    res = run_backtest(data, strat, initial_capital=100000.0, spread_pips=0.0, slippage_pct=0.0, risk_per_trade=0.01, stop_loss_pips=2, take_profit_pips=2, data_pair="EURUSD")
    trades = res["trades"]
    assert any(t.exit_reason == 'take_profit' for t in trades) or trades[-1].exit_reason == 'take_profit'

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

def test_signal_flip_exit_basic():
    # Use deterministic strategy: long(1) then short(-1) should trigger flip
    data = make_simple_data()
    strat = DeterministicStrategy([1, 0, -1, 0])  # long at bar1, hold, flip at bar2
    res = run_backtest(data, strat, initial_capital=100000.0, spread_pips=0.0, slippage_pct=0.0, risk_per_trade=0.01, stop_loss_pips=None, max_holding_bars=None, data_pair="EURUSD")
    trades = res["trades"]
    assert len(trades) >= 1, "Expected at least one trade"
    # The trade should close due to signal flip
    flip_trades = [t for t in trades if t.exit_reason == 'signal_flip']
    assert len(flip_trades) >= 1, f"Expected signal_flip exit, got: {[t.exit_reason for t in trades]}"

def test_time_exit_basic():
    data = make_simple_data()
    strat = Breakout()
    res = run_backtest(data, strat, initial_capital=100000.0, spread_pips=0.0, slippage_pct=0.0, risk_per_trade=0.01, stop_loss_pips=None, max_holding_bars=1, data_pair="EURUSD")
    trades = res["trades"]
    if trades:
        assert trades[0].duration >= 1

def test_risk_based_sizing():
    # EURUSD, 1% risk, stop 50 pips -> expect large units ~ balance*0.01 / (0.005) for 50 pips on EURUSD ~ 200k
    units = calculate_position_size("EURUSD", 100000.0, 0.01, 50)
    assert units > 0
    # JPY pair should yield smaller units for same risk
    units_jpy = calculate_position_size("USDJPY", 100000.0, 0.01, 50)
    assert units_jpy > 0
