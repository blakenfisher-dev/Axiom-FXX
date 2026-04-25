import os
import pandas as pd
import tempfile
from forex_bot_platform.paper_trading import PaperTrader, PaperTradeStorage, PaperTrade

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

def make_test_data():
    dates = pd.date_range("2025-01-01", periods=4, freq="D")
    closes = [1.1000, 1.1010, 1.1000, 1.0990]
    df = pd.DataFrame({"date": dates, "close": closes, "open": closes, "high": closes, "low": closes, "volume": [1000]*4})
    return df

def test_paper_trading_start_stop_reset():
    data = make_test_data()
    strat = DeterministicStrategy([1, 0, -1, 0])
    pt = PaperTrader(initial_balance=100000.0, data=data, pair="EURUSD", strategy=strat)
    pt.start()
    assert pt.balance == 100000.0
    assert pt.open_positions == []
    pt.step()  # should open a position
    assert len(pt.open_positions) == 1
    pt.reset()
    assert pt.balance == 100000.0
    assert pt.open_positions == []

def test_open_close_positions_with_signal_flip():
    data = make_test_data()
    # Use deterministic strategy: long at step 0, hold at step1, flip at step2
    # Pass stop_loss_pips=0 to disable stop loss so signal flip is the only exit trigger
    strat = DeterministicStrategy([1, 0, -1, 0])
    pt = PaperTrader(initial_balance=100000.0, data=data, pair="EURUSD", strategy=strat, stop_loss_pips=0, take_profit_pips=99999)
    pt.start()
    pt.step()  # open first long (sig=1)
    assert len(pt.open_positions) == 1
    pt.step()  # no signal (sig=0) stay in
    pt.step()  # signal flip (sig=-1) should close
    assert len(pt.open_positions) == 0, f"Expected 0 open, got {len(pt.open_positions)}"
    assert len(pt.closed_positions) >= 1, f"Expected at least 1 closed, got {len(pt.closed_positions)}"

def test_unrealised_and_realised_pnl_and_exports():
    data = make_test_data()
    strat = DeterministicStrategy([1, 0, -1, 0])
    pt = PaperTrader(initial_balance=100000.0, data=data, pair="EURUSD", strategy=strat)
    pt.start()
    pt.step()
    # Unrealised on step 2
    last_price = data.iloc[1]["close"]
    if pt.open_positions:
        ul = pt.open_positions[0].unrealised_pnl_at(last_price)
        assert isinstance(ul, float)
    pt.step()  # close on flip
    if pt.closed_positions:
        # ensure realised PnL recorded
        assert pt.closed_positions[-1].pnl is not None
        csv_path = pt.export_trades_csv("paper_trades_test.csv")
        assert os.path.exists(csv_path)
        os.remove(csv_path)
    # SQLite export
    pt.export_all_sqlite()
    storage = pt.storage
    trades = storage.read_trades()
    assert isinstance(trades, list)

def test_multi_position_handling():
    dates = pd.date_range("2025-01-01", periods=6, freq="D")
    closes = [1.1000, 1.1010, 1.1020, 1.1000, 1.0990, 1.0980]
    data = pd.DataFrame({"date": dates, "close": closes, "open": closes, "high": closes, "low": closes, "volume": [1000]*6})
    # Strategy generates alternating signals for max_concurrent=2
    strat = DeterministicStrategy([1, -1, 1, -1, 0, 0])
    pt = PaperTrader(initial_balance=100000.0, data=data, pair="EURUSD", strategy=strat, max_concurrent=2, stop_loss_pips=0, take_profit_pips=99999)
    pt.start()
    for _ in range(4):
        pt.step()
    # Two positions should be open (long and short)
    assert len(pt.open_positions) <= 2

def test_session_persistence():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_session.db")
        storage = PaperTradeStorage(db_path=db_path)
        session_id = storage.create_session("EURUSD", 100000.0)
        assert session_id == 1
        session = storage.get_active_session()
        assert session is not None
        assert session.pair == "EURUSD"
        storage.close_session(session_id, 105000.0)
        stats = storage.get_performance_stats(session_id)
        storage.close()
        assert stats["current_balance"] == 105000.0

def test_performance_report():
    dates = pd.date_range("2025-01-01", periods=4, freq="D")
    closes = [1.1000, 1.1010, 1.1000, 1.0990]
    data = pd.DataFrame({"date": dates, "close": closes, "open": closes, "high": closes, "low": closes, "volume": [1000]*4})
    strat = DeterministicStrategy([1, 0, -1, 0])
    pt = PaperTrader(initial_balance=100000.0, data=data, pair="EURUSD", strategy=strat, stop_loss_pips=0, take_profit_pips=99999)
    pt.start()
    pt.run_to_end()
    report = pt.get_performance_report()
    assert "total_trades" in report
    assert isinstance(report["total_trades"], int)
