import pandas as pd

def trending_market_fixture():
    dates = pd.date_range("2025-01-01", periods=8, freq="D")
    opens = [100.0, 100.5, 101.0, 101.5, 102.5, 103.0, 104.0, 105.0]
    highs = [o + 0.5 for o in opens]
    lows = [o - 0.5 for o in opens]
    closes = [100.4, 101.2, 102.0, 102.8, 103.9, 104.6, 105.4, 106.2]
    vols = [1000, 1100, 1050, 1200, 1300, 1250, 1400, 1500]
    return pd.DataFrame({"date": dates, "open": opens, "high": highs, "low": lows, "close": closes, "volume": vols})

def ranging_market_fixture():
    dates = pd.date_range("2025-01-01", periods=8, freq="D")
    opens = [1.1000]*8
    highs = [1.1005]*8
    lows = [1.0995]*8
    closes = [1.1002, 1.1003, 1.1001, 1.1004, 1.1002, 1.1001, 1.1003, 1.1002]
    vols = [800, 820, 780, 900, 860, 840, 920, 880]
    return pd.DataFrame({"date": dates, "open": opens, "high": highs, "low": lows, "close": closes, "volume": vols})

def volatile_breakout_market_fixture():
    dates = pd.date_range("2025-01-01", periods=9, freq="D")
    opens = [1.2000, 1.2000, 1.2000, 1.2000, 1.2000, 1.2100, 1.2150, 1.2250, 1.2400]
    highs = [o + 0.002 for o in opens]
    lows = [o - 0.003 for o in opens]
    closes = [1.2002, 1.2005, 1.2010, 1.2030, 1.2040, 1.2120, 1.2200, 1.2350, 1.2480]
    vols = [1000+i*50 for i in range(9)]
    return pd.DataFrame({"date": dates, "open": opens, "high": highs, "low": lows, "close": closes, "volume": vols})

def stop_loss_hit_fixture():
    dates = pd.date_range("2025-01-01", periods=7, freq="D")
    opens = [1.1000, 1.1002, 1.1005, 1.1010, 1.1005, 1.0995, 1.0990]
    highs = [o + 0.0005 for o in opens]
    lows = [o - 0.0005 for o in opens]
    closes = [1.1002, 1.1010, 1.1006, 1.0999, 1.0992, 1.0980, 1.0975]
    vols = [1000]*7
    return pd.DataFrame({"date": dates, "open": opens, "high": highs, "low": lows, "close": closes, "volume": vols})

def take_profit_hit_fixture():
    dates = pd.date_range("2025-01-01", periods=7, freq="D")
    opens = [1.3000, 1.3002, 1.3004, 1.3006, 1.3010, 1.3020, 1.3035]
    highs = [o + 0.001 for o in opens]
    lows = [o - 0.001 for o in opens]
    closes = [1.3005, 1.3015, 1.3020, 1.3028, 1.3030, 1.3032, 1.3045]
    vols = [1000]*7
    return pd.DataFrame({"date": dates, "open": opens, "high": highs, "low": lows, "close": closes, "volume": vols})

def signal_flip_fixture():
    dates = pd.date_range("2025-01-01", periods=6, freq="D")
    opens = [1.1500]*6
    highs = [1.1510]*6
    lows = [1.1490]*6
    # Ensure a flip occurs by moving to a price below the prior low on a later bar
    closes = [1.1505, 1.1515, 1.1480, 1.1475, 1.1470, 1.1465]
    vols = [1000]*6
    return pd.DataFrame({"date": dates, "open": opens, "high": highs, "low": lows, "close": closes, "volume": vols})
