import numpy as np
import pandas as pd
from forex_bot_platform.backtesting.metrics import compute_metrics

def test_compute_metrics_basic():
    # Build a simple increasing equity path
    equity = pd.Series([1000, 1010, 1025, 1050, 1100, 1200], dtype=float)
    metrics = compute_metrics(equity)
    assert "total_return_pct" in metrics
    assert metrics["total_return_pct"] > 0
    assert "sharpe" in metrics
