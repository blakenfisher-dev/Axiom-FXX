from forex_bot_platform.risk.risk_manager import calculate_position_size, is_jpy_pair

def test_position_size_calculation():
    # Test EURUSD (non-JPY)
    units = calculate_position_size("EURUSD", 100000, 0.01, 50)
    assert units > 0
    # Test USDJPY (JPY pair)
    units_jpy = calculate_position_size("USDJPY", 100000, 0.01, 50)
    assert units_jpy > 0
    # Zero balance returns 0
    assert calculate_position_size("EURUSD", 0, 0.01, 50) == 0
