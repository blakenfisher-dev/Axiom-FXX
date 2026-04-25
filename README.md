# Forex Bot Platform

A professional forex trading bot with Backtest, Demo, and Live trading modes.

## Trading Modes

### 1. Backtest Mode
Test strategies on historical data. No real money, no broker connection.

### 2. Demo Trading Mode
Connect to MT5 demo accounts only. Uses live market data with fake money.

### 3. Live Trading Mode
Real-money trading. **DISABLED by default** until explicit approval.
Requires: approval file + config flag + runtime flag + all safety gates.

## Setup (Windows PowerShell)

```powershell
# Clone or download
cd forex-bot-platform

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt
```

## Commands

### Run Tests
```powershell
python -m pytest -q
```

### Run Backtest
```powershell
python -m forex_bot_platform.main --pair EURUSD --strategy Breakout --timeframe 1h
```

### Demo Dry Run
```powershell
python -m forex_bot_platform.main --demo-dry-run --login YOUR_LOGIN --server YOUR_SERVER
```

### Demo Soak Test
```powershell
python -m forex_bot_platform.main --demo-soak --login YOUR_LOGIN --server YOUR_SERVER
```

### Live Readiness Check
```powershell
python -m forex_bot_platform.main --live-readiness
```

### Launch Dashboard
```powershell
streamlit run forex_bot_platform/dashboard/app.py
```

### Run Menu
```powershell
.\run_bot_menu.ps1
```

## Safety Warnings

- **No profit is guaranteed**
- Trading forex involves significant risk of loss
- Past backtest results do not guarantee future profits
- Live trading requires explicit approval
- All live orders require stop-loss
- Emergency stop is available

## Project Structure

```
forex-bot-platform/
  forex_bot_platform/
    main.py           # CLI entry point
    config/           # Configuration
    data/            # Market data
    strategies/      # Trading strategies
    backtesting/    # Backtest engine
    risk/            # Risk management
    execution/      # MT5 execution
    dashboard/       # Streamlit dashboard
    reports/        # Report generation
    logs/           # Log files
  tests/            # Test suite
  README.md
  PROJECT_STATUS.md
  DEMO_TRADING_RUNBOOK.md
  LIVE_TRADING_RUNBOOK.md
  PHASE4_LIVE_TRADING_PLAN.md
  requirements.txt
  run_bot_menu.ps1
  run_health.ps1
  run_demo_health.ps1
  run_phase4_health.ps1
```

## License

MIT - Use at your own risk.