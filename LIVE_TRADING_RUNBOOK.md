# LIVE TRADING RUNBOOK

**WARNING: This runbook covers REAL MONEY trading.**

This document explains how to safely use Live Trading Mode.

---

## ⚠️ IMPORTANT DISCLAIMERS

- **Live Trading Mode uses REAL MONEY**
- You can and WILL lose money
- No profit guarantees
- No martingale or grid trading
- No doubling after losses
- Live trading is DISABLED BY DEFAULT

---

## Pre-Live Checklist

Before enabling Live Trading Mode, you MUST verify:

- [ ] Demo Trading Mode is fully tested and stable
- [ ] All `run_phase3_health.ps1` checks pass
- [ ] You have read and understood this runbook
- [ ] You understand the risks
- [ ] You have created LIVE_APPROVAL.json with your name

---

## Live Trading Flow

### Step 1: Create Approval File

Create `LIVE_APPROVAL.json`:

```json
{
    "approver_name": "Your Name",
    "approval_timestamp": "2026-04-25T12:00:00Z",
    "account_number": "12345678",
    "broker_server": "MetaQuotes-Demo",
    "max_account_size": 10000,
    "max_risk_per_trade": 0.0025,
    "max_daily_loss": 0.01,
    "max_weekly_loss": 0.03,
    "max_drawdown": 0.05,
    "max_open_positions": 3,
    "user_acknowledges_risk": true
}
```

### Step 2: Check Readiness

```powershell
python -m forex_bot_platform.main --live-readiness
```

This checks:
- Approval file exists and is valid
- Approval not expired (30 days)
- Risk limits defined
- Emergency stop not active
- Configuration valid

### Step 3: Dry Run (OPTIONAL)

```powershell
python -m forex_bot_platform.main --login 12345 --password demo --server MetaQuotes-Demo --live-dry-run
```

This verifies:
- Can connect to broker
- Safety gates pass
- But places NO orders

### Step 4: Enable Live Trading

```powershell
python -m forex_bot_platform.main --enable-live-trading
```

**This does NOT place orders!**

### Step 5: Place Live Order

```powershell
python -m forex_bot_platform.main --login 12345 --password demo --server MetaQuotes-Demo --enable-live-trading --place-live-order --pair EURUSD --stop-loss 1.0850
```

**Requires:**
- `--enable-live-trading` flag
- Valid LIVE_APPROVAL.json
- Stop-loss on EVERY order
- All safety gates pass

---

## Safety Gates

All gates must pass before ANY live order:

| Gate | Description |
|------|-------------|
| live_enabled | Live trading explicitly enabled |
| approval | Valid human approval exists |
| account | Account matches approval |
| emergency | Emergency stop NOT active |
| connection | Connected to broker |
| market_data | Market data available |
| risk_limits | Within risk limits |

Order gates:

| Gate | Description |
|------|-------------|
| stop_loss | Stop-loss required |
| risk_per_trade | Within 0.5% max |
| max_positions | Under 3 positions |
| spread | Under 3 pips |
| duplicate | No duplicate order |
| session | Trading session open |

---

## Risk Limits

Default conservative limits:

| Limit | Default | Hard Max |
|-------|---------|----------|
| Risk per trade | 0.25% | 0.5% |
| Max daily loss | 1% | - |
| Max weekly loss | 3% | - |
| Max drawdown | 5% | - |
| Max positions | 3 | - |
| Max spread | 3 pips | - |

---

## Emergency Stop

If things go wrong:

```powershell
python -m forex_bot_platform.main --emergency-stop-live
```

This:
- Disables live trading immediately
- Closes all open positions (if configured)
- Logs emergency stop event
- Requires manual reset to re-enable

---

## Audit Logs

Every live trading event is logged to `live_trading_audit.log`:

- Connection attempts
- Account verification
- Approval verification
- Order attempts
- Order rejections
- Order successes/failures
- Emergency stops
- Safety breaches

---

## Dashboard

The dashboard has a Live Trading section but it is hidden until enabled.

Features:
- Live status (enabled/disabled)
- Account info
- Approval status
- Safety checklist
- Risk limits
- Open positions
- Order history
- Audit log viewer
- **EMERGENCY STOP BUTTON**

---

## Commands Summary

| Command | Description |
|---------|-------------|
| `--live-readiness` | Check if ready (no order) |
| `--live-dry-run` | Verify safety (no order) |
| `--enable-live-trading` | Enable live mode |
| `--place-live-order` | Place actual order |
| `--emergency-stop-live` | Emergency stop |

---

## Troubleshooting

### "Live trading is not enabled"

Run with `--enable-live-trading` flag.

### "No valid live trading approval"

Create `LIVE_APPROVAL.json` file.

### "Stop-loss is required"

Every live order MUST have a stop-loss.

### "Risk per trade exceeds limit"

Reduce position size or stop-loss distance.

### "Max positions reached"

Close an existing position first.

---

## Rollback

If live trading issues occur:

1. Run `--emergency-stop-live` immediately
2. Close positions manually in MT5
3. Investigate logs in `live_trading_audit.log`
4. Fix issues
5. Re-run `--live-readiness`
6. Try dry run again
7. Only then enable live mode

---

## Support

- Check `live_trading_audit.log` for events
- Check `live_risk_state.json` for P&L
- Review `PHASE4_LIVE_TRADING_PLAN.md`

---

**REMEMBER: You are trading with REAL MONEY.**