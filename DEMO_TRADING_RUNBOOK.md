# Demo Trading Runbook

This runbook provides step-by-step instructions for verifying Demo Trading Mode before any live trading.

## Prerequisites

- Python 3.10+ with venv activated
- MT5 platform installed
- Demo account created
- MetaTrader5 Python package installed

## Quick Verification

### 1. Run Demo Health Check

```powershell
.\venv\Scripts\activate
powershell -ExecutionPolicy Bypass -File run_demo_health.ps1
```

Expected output: 8/8 PASS

---

## Manual Verification Steps

### Step 1: Create Demo Account

1. Open MetaTrader 5
2. File → Open an Account
3. Select broker with "Demo" suffix
4. Complete registration with $10,000+ deposit
5. Note Login number and Server name

### Step 2: Enable Algo Trading

1. Tools → Options → Expert Advisors
2. Check "Allow live trading"
3. Check "Allow DLL imports"
4. Click OK

### Step 3: Install Python Package

```powershell
pip install MetaTrader5
```

### Step 4: Test Connection

Open Python and run:

```python
import MetaTrader5 as mt5
mt5.initialize()
account = mt5.account_info()
print(f"Account: {account.login}")
print(f"Server: {account.server}")
print(f"Balance: {account.balance}")
mt5.shutdown()
```

---

## Dashboard Verification

### Start Dashboard

```powershell
streamlit run forex_bot_platform/dashboard/app.py
```

### Demo Trading Checklist

In the dashboard, verify:

- [ ] Mode selector shows "Demo Trading"
- [ ] Connect button visible
- [ ] Login input field
- [ ] Password input field (masked)
- [ ] Server input field

### Connect to Demo

1. Enter Login from Step 1
2. Enter Password
3. Enter Server (e.g., "MetaQuotes-Demo")
4. Click "Connect to MT5 Demo"

### Verify Connection

After connecting, verify:

- [ ] "DEMO" badge shows in Account Type
- [ ] Balance displays correctly
- [ ] Live tick shows for selected symbol
- [ ] Safety panel shows status
- [ ] Emergency STOP button is visible

---

## Dry Run Test

### Run Without Placing Order

```powershell
python -m forex_bot_platform.main --demo-dry-run --login YOUR_LOGIN --server YOUR_SERVER
```

This will:
- Connect to MT5
- Verify demo account
- Get symbol info
- Get latest tick
- Validate safety config
- Report status WITHOUT placing order

Expected output: "Dry run complete. No orders placed."

### Run WITH Demo Order

```powershell
python -m forex_bot_platform.main --demo-dry-run --place-demo-order --login YOUR_LOGIN --server YOUR_SERVER
```

This will:
- Do everything above
- THEN place a demo order

**WARNING**: Only use `--place-demo-order` if you want to test actual demo placement.

---

## Safety Verification

### 1. Demo Account Verification

Try connecting with a LIVE server. Should fail:

```
Live account detected (live). Demo Trading Mode requires demo account only.
```

### 2. Stop-Loss Required

Try placing order without stop-loss. Should fail:

```
Stop-loss required for demo trading
```

### 3. Max Daily Loss

Make a losing trade that exceeds $1000 daily loss. Next order should fail:

```
Max daily loss reached: -$1000.00
```

### 4. Emergency Stop

Click Emergency STOP button. Should:
- Close all positions
- Disconnect from MT5
- Block further orders

---

## Common Issues

### "Connection failed"

| Cause | Solution |
|-------|----------|
| Wrong server | Verify exact server name in MT5 |
| Wrong password | Reset in MT5 |
| Firewall | Allow MT5 through firewall |
| Broker downtime | Try different time |

### "Live account detected"

| Cause | Solution |
|-------|----------|
| Using live server | Use demo server |
| Broker uses same server | Check account login |

### "Spread too high"

| Cause | Solution |
|-------|----------|
| Off-market hours | Wait for market open |
| Low liquidity | Use major pairs (EURUSD) |

---

## Security Checklist

Before using Demo Trading Mode:

- [ ] Using DEMO account (not LIVE)
- [ ] Algo trading enabled in MT5
- [ ] Demo account balance is play money
- [ ] Stop-loss enabled in SafetyConfig
- [ ] Max daily loss set to acceptable amount
- [ ] Emergency STOP button is accessible
- [ ] No real credentials stored in code
- [ ] Dashboard runs without errors

---

## Rollback Procedure

If Demo Trading Mode behaves unexpectedly:

1. Click **Emergency STOP** immediately
2. Close all MT5 positions manually in MT5 platform
3. Disconnect dashboard
4. Restart dashboard
5. Verify account is DEMO type
6. Contact support if issues persist

---

## Testing Checklist

Complete this checklist before enabling Live Trading Mode:

- [ ] Health check passes (8/8)
- [ ] Demo account connects successfully
- [ ] Demo account type shows "DEMO"
- [ ] Symbol tick updates live
- [ ] Safety panel shows correct values
- [ ] Emergency STOP closes all positions
- [ ] Max daily loss triggers correctly
- [ ] Unknown account blocks correctly
- [ ] Audit log records all actions
- [ ] Rejection report captures blocked orders

---

## Next Steps

After completing all verification:

1. **DO NOT enable Live Trading Mode**
2. Mark Phase 3.3 as complete in PROJECT_STATUS.md
3. Proceed to Phase 4 only when explicitly approved