# Pre-Live Trading Review Checklist

This checklist must be completed BEFORE enabling live trading mode.

## Phase 1: Backtest Validation

- [ ] Run backtest on EURUSD 1h with Breakout strategy (minimum 1000 candles)
- [ ] Verify Sharpe ratio > 1.0
- [ ] Verify max drawdown < 20%
- [ ] Verify win rate > 40%
- [ ] Run backtest on GBPUSD 1h (different pair validation)
- [ ] Run backtest on USDJPY 1h (different pair validation)

## Phase 2: Demo Trading Dry Run

- [ ] Connect to MT5 demo account successfully
- [ ] Verify market data streams correctly
- [ ] Verify order placement works (dry run mode)
- [ ] Verify stop-loss is attached to all orders
- [ ] Verify take-profit works
- [ ] Verify order modification works
- [ ] Verify order cancellation works

## Phase 3: Demo Soak Test

- [ ] Run 1-hour soak test with max 10 trades
- [ ] Verify no crashes or hangs
- [ ] Verify order fills complete correctly
- [ ] Verify P&L calculation is accurate
- [ ] Verify trade logging works
- [ ] Verify emergency stop works

## Phase 4: Live Readiness

- [ ] Complete Phase 1-3 checklist items
- [ ] No approval file exists in ./approvals/ directory
- [ ] config/settings.py: LIVE_MODE_ENABLED = False (default)
- [ ] No runtime flag --live-trade passed
- [ ] Emergency stop mechanism tested

## Safety Gates

- [ ] Live trading requires ALL of:
  - [ ] Approval file in ./approvals/ directory (e.g., APPROVAL_20260101.md)
  - [ ] config/settings.py: LIVE_MODE_ENABLED = True
  - [ ] Command line: --live-trade flag
  - [ ] No emergency stop in effect
- [ ] No broker credentials stored in plain text
- [ ] No order without stop-loss
- [ ] No martingale strategy
- [ ] No grid trading
- [ ] No doubling after losses

## Risk Limits

- [ ] Max daily loss: $1,000 (demo), $500 (live)
- [ ] Max open trades: 3
- [ ] Max position size: 0.1 lot
- [ ] Require stop-loss on all trades
- [ ] Require take-profit on all trades

## Approval Requirements

Live trading approval requires:

1. All checklist items completed
2. Approval file with:
   - Date of approval
   - Account number (last 4 digits only)
   - Approved by (name)
   - Max risk amount
3. All safety gates verified

## Emergency Procedures

- [ ] Emergency stop command tested: python -m forex_bot_platform.main --emergency-stop-live
- [ ] All open positions can be closed manually
- [ ] Account balance can be verified
- [ ] Broker support contact available