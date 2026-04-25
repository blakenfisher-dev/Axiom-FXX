# PROJECT_STATUS

## Three Trading Modes

### 1. Backtest Mode
- Uses historical real market data
- Default test period: 1 year ago to today
- Runs selected strategy against historical candles
- Shows performance metrics, equity curve, drawdown, trade log, win rate, profit factor and return
- No broker orders are placed
- No real money is used
- **Status: ACTIVE**

### 2. Demo Trading Mode
- Uses live real market data
- Connects to an MT5/broker demo account
- Places demo orders only
- Uses fake/demo money
- Must verify the account is demo before placing any order
- Must block live/real accounts
- **Status: ACTIVE - READY FOR HUMAN REVIEW**

### 3. Live Trading Mode
- Uses live real market data
- Connects to a real broker account
- Places real orders with real money
- Must remain disabled until Demo Trading Mode is stable and fully tested
- Must require explicit manual enablement, risk confirmation and safety checks
- **Status: DISABLED**

---

## Current Project Status

- **Backtest Mode**: ACTIVE
- **Internal Simulation**: ACTIVE/SCAFFOLDED (app-only simulated trades with no broker)
- **Demo Trading Mode**: ACTIVE - READY FOR HUMAN REVIEW (Phase 3 complete)
- **Live Trading Mode**: IMPLEMENTED - PHASE 4 COMPLETE - DISABLED BY DEFAULT

---

## Phase 2.x Summary

## Phase 3 (COMPLETE)

Demo Trading Mode is fully implemented, tested, documented, and ready for human review.

### Phase 3.5 (Final)
- Demo readiness evaluator
- Readiness report generation (JSON + Markdown)
- Readiness scoring with pass/fail gates
- Phase 3 final health script

### Phase 3.4
- Demo soak-test mode with heartbeat
- Safety status tracking
- Report outputs (JSON, CSV, audit log)

### Phase 3.3
- Demo dry run command
- Demo health check script
- Demo Trading runbook

### Phase 3.2
- Audit logs
- Rejection report
- Session persistence
- Cooldown and max trades per day

### Phase 3.1
- Dashboard integration
- Demo order form
- Safety panel

### Phase 3.0
- MT5DemoExecutor with demo account detection
- Safety checks (stop-loss required, max daily loss, spread, etc.)
- Live account blocking

---

## Current Status (Phase 3 COMPLETE)

### Phase 2.9.1 (Locked)
- Signal flip exit fixes
- Stop-loss/take-profit handling improvements
- All tests pass

### Phase 2.9 (Locked)
- Paper trading hardening with SQLite
- Concurrent positions
- Per-trade stop/TP
- Dashboard integration
- Unrealised/realised P&L
- CSV/SQLite export

### Phase 2.8.2 (Locked)
- Structural cleanup
- Paper trading scaffold moved to forex_bot_platform/
- Dashboard moved to forex_bot_platform/
- Data quality moved to forex_bot_platform/

### Phase 2.8.1 (Locked)
- Run scripts (PowerShell)
- Smoke tests
- Dashboard improvements

### Phase 2.8 (Locked)
- Dashboard integration
- Paper trading scaffold
- Data quality score

### Phase 2.7 (Locked)
- Deterministic fixtures
- Data validation
- Research engine hardening

### Phase 2.6 (Locked)
- Risk-based position sizing
- Data quality checks
- CLI output improvements

### Phase 2.5 (Locked)
- Real data via yfinance
- Improved strategies
- Spread/slippage
- Stop-loss/take-profit exits

### Phase 2 (Locked)
- Core backtesting engine
- Strategies
- Dashboard scaffold
- Research engine

---

## Guardrails (Always Active)

- No real-money trading
- Demo accounts only for Demo Trading Mode
- Live accounts must be blocked
- No broker credentials stored in plain text
- Stop-loss required on every order
- Spread check required
- Max daily loss check required
- Max open trades check required
- Emergency stop required

---

## File Structure

```
forex-bot-platform/
  requirements.txt
  README.md
  PROJECT_STATUS.md
  forex_bot_platform/
    __init__.py
    main.py
    config/
    data/
    strategies/
    backtesting/
    risk/
    execution/         # MT5 scaffold - disabled
    dashboard/
    paper_trading.py  # Internal simulation
    research_engine/
  tests/
  run_*.ps1 scripts
```

---

## Commands

- Backtest: `python -m forex_bot_platform.main --pair EURUSD --strategy Breakout --timeframe 1h`
- Demo dry run: `python -m forex_bot_platform.main --login 12345 --demo-dry-run`
- Demo readiness: `python -m forex_bot_platform.main --demo-readiness --soak-dir .`
- Live readiness: `python -m forex_bot_platform.main --live-readiness`
- Dashboard: `streamlit run forex_bot_platform/dashboard/app.py`
- Tests: `pytest -q`
- Health: `powershell -ExecutionPolicy Bypass -File run_health.ps1`
- Phase 4 health: `powershell -ExecutionPolicy Bypass -File run_phase4_health.ps1`

---

## Phase 4 (COMPLETE)

Live Trading Mode with full safety controls.

### Features Implemented
- Live executor with account functions
- Live guard with safety gates (7 pre-order gates + order gates)
- Live safety with conservative risk limits
- Live audit logger for all events
- Live readiness checker

### Safety Features
- Live mode DISABLED BY DEFAULT
- Human approval required (LIVE_APPROVAL.json)
- All 7 safety gates enforced
- Order-level gates (stop-loss required, risk limits, max positions, spread check)
- Emergency stop capability
- Conservative defaults (0.25% risk/trade, 1% daily loss max)

### CLI Commands
- `--live-readiness`: Check if ready (no order)
- `--live-dry-run`: Verify safety (no order)
- `--enable-live-trading`: Enable live mode
- `--place-live-order`: Place actual order (requires enable)
- `--emergency-stop-live`: Emergency stop

### Test Results
- 118/118 tests pass
- run_health.ps1: PASS
- run_phase4_health.ps1: PASS

---

## Next Phase

**Phase 5: Future Enhancements**

(Subject to future requirements)