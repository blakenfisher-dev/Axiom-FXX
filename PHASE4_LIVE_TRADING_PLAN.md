# Phase 4: Live Trading Mode - Planning Document

**IMPORTANT**: Live Trading Mode is currently **DISABLED**. This document is a planning reference only.

---

## 1. Objective

Enable live trading with real money on a broker MT5 account, subject to strict safety limits and human oversight.

---

## 2. Required Preconditions

Before Live Trading Mode can be enabled:

- [ ] Demo Trading Mode has been tested for minimum 30 days
- [ ] Demo Trading Readiness Report shows PASSED (`READY_FOR_LIVE_REVIEW = true`)
- [ ] All Phase 3 health checks pass
- [ ] Human operator has reviewed demo soak test results
- [ ] Risk parameters have been set and verified
- [ ] Broker account verification completed

---

## 3. Required Human Approvals

- [ ] Senior risk approval required
- [ ] Account owner consent documented
- [ ] Initial capital limit approved
- [ ] Max loss limits approved

---

## 4. Account-Size Limits

| Phase | Max Account Size |
|-------|-----------------|
| Pilot | $1,000 |
| Early | $5,000 |
| Established | $25,000 |
| Full | >$25,000 (requires additional approval) |

---

## 5. Max Risk-Per-Trade Limits

- Default: 1% of account equity per trade
- Maximum: 2% of account equity per trade
- Minimum: 0.5% (to ensure meaningful position size)

---

## 6. Max Daily Loss Limits

| Phase | Max Daily Loss |
|-------|----------------|
| Pilot | $50 |
| Early | $200 |
| Established | $1,000 |
| Full | 5% of account |

Trading halts for the day when limit is hit.

---

## 7. Max Weekly Loss Limits

| Phase | Max Weekly Loss |
|-------|-----------------|
| Pilot | $100 |
| Early | $500 |
| Established | $2,500 |
| Full | 10% of account |

Trading halts for the week when limit is hit.

---

## 8. Max Drawdown Limits

| Phase | Max Drawdown |
|-------|--------------|
| Pilot | 10% |
| Early | 15% |
| Established | 20% |
| Full | 25% |

System disables all trading when drawdown limit is hit.

---

## 9. Max Open Positions

- Default: 3 concurrent positions
- Maximum: 5 concurrent positions
- Same symbol: Maximum 1 position per symbol

---

## 10. Max Exposure Per Currency

| Phase | Max Exposure |
|-------|--------------|
| Pilot | $500 |
| Early | $2,000 |
| Established | $10,000 |
| Full | $50,000 |

---

## 11. Broker/Account Verification Requirements

Before live trading:

- [ ] Verify broker is regulated
- [ ] Verify account is LIVE (not demo)
- [ ] Verify account login credentials are stored encrypted
- [ ] Verify account has sufficient margin
- [ ] Verify stop-loss is mandatory on all orders

---

## 12. Kill Switch Requirements

- Manual kill switch available in dashboard
- Automatic kill switch triggers on:
  - Daily loss limit hit
  - Weekly loss limit hit
  - Max drawdown limit hit
  - Emergency stop activated
  - Connection lost for >5 minutes

Kill switch must:
- Close all open positions immediately
- Disconnect from broker
- Log the event
- Require human intervention to reset

---

## 13. Audit Logging Requirements

All live trading events must be logged:

- Connection/disconnection
- Order placed (with price, SL, TP)
- Order closed (with P&L)
- Order modified
- Kill switch triggered
- Limit hit
- Error/exception

Log format:
```
TIMESTAMP | EVENT_TYPE | DETAILS | RESULT
```

---

## 14. Error/Reconnect Handling

- Connection lost: Attempt reconnect up to 3 times
- Reconnect interval: 30 seconds
- After 3 failures: Trigger kill switch
- Order fill timeout: 30 seconds
- Invalid order response: Log error, do not retry automatically

---

## 15. Duplicate Order Prevention

- Track all open orders by symbol + side
- Reject duplicate order if same symbol + side already open
- Require manual close of existing position before new order

---

## 16. News/Spread/Session Filters

- Block trading during major news events (configurable)
- Block trading when spread > 5 pips (configurable)
- Block trading during market close (Saturday/Sunday)
- Block trading during broker maintenance (configurable)

---

## 17. Rollback Plan

If Live Trading Mode fails:

1. Activate kill switch immediately
2. Close all positions manually in MT5
3. Document incident
4. Switch back to Demo Trading Mode
5. Review logs and identify failure
6. Get human approval before re-enabling

---

## 18. Minimum Demo Soak-Test Requirements

Before Live Trading can be enabled:

- [ ] Minimum 7 days of continuous demo soak testing
- [ ] At least 50 demo orders placed
- [ ] Zero live-account bypass attempts
- [ ] Zero emergency stops triggered
- [ ] Demo readiness score >= 80
- [ ] All safety checks passed consistently

---

## 19. Live Pilot Rules

Initial live trading (Pilot phase):

- Max account: $1,000
- Max daily loss: $50
- Max risk per trade: 1%
- Max open positions: 1
- Require human approval for each trading day

---

## 20. Clear Statement

**Live Trading Mode is currently DISABLED.**

This document is for planning purposes only. Live trading requires:
- Explicit human approval
- Successful demo testing
- Signed risk acknowledgment
- Regulatory compliance verification

**Do not enable Live Trading Mode without proper authorization.**

---

## Phase 4 Not Started

This plan is pending review. Phase 4 development has not begun.

Current status:
- Phase 3: COMPLETE
- Phase 4: NOT STARTED
- Live Trading Mode: DISABLED