from forex_bot_platform.research_engine.experiment_runner import run_experiments
import pandas as pd

def test_run_experiments_basic():
    # This will run with defaults; it should return a list of results
    results = run_experiments(pair="EURUSD", timeframe="1h", experiments=1, strategy=None, all_strategies=False, all_pairs=False)
    assert isinstance(results, list)
