param()

Write-Host "=== Demo Trading Health Check ===" -ForegroundColor Cyan
Write-Host ""

$results = @()

# Test using pytest
Write-Host "[1] Running demo tests..." -NoNewline
try {
    python -m pytest tests/test_dashboard_demo.py -q --tb=no 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "PASS" -ForegroundColor Green
        $results += "PASS"
    } else {
        Write-Host "FAIL" -ForegroundColor Red
        $results += "FAIL"
    }
} catch {
    Write-Host "FAIL" -ForegroundColor Red
    $results += "FAIL"
}

# Test import
Write-Host "[2] Testing MT5 import..." -NoNewline
try {
    python -c "from forex_bot_platform.execution.mt5_executor import MT5DemoExecutor" 2>$null
    Write-Host "PASS" -ForegroundColor Green
    $results += "PASS"
} catch {
    Write-Host "FAIL" -ForegroundColor Red
    $results += "FAIL"
}

# Test demo connect
Write-Host "[3] Testing demo connect..." -NoNewline
try {
    python -c "from forex_bot_platform.execution.mt5_executor import MT5DemoExecutor,SafetyConfig; e=MT5DemoExecutor(login='x',password='x',server='Demo',safety_config=SafetyConfig()); e.connect(); assert e.is_connected" 2>$null
    Write-Host "PASS" -ForegroundColor Green
    $results += "PASS"
} catch {
    Write-Host "FAIL" -ForegroundColor Red
    $results += "FAIL"
}

# Test safety config
Write-Host "[4] Testing safety config..." -NoNewline
try {
    python -c "from forex_bot_platform.execution.mt5_executor import SafetyConfig; c=SafetyConfig(); assert c.max_daily_loss==1000" 2>$null
    Write-Host "PASS" -ForegroundColor Green
    $results += "PASS"
} catch {
    Write-Host "FAIL" -ForegroundColor Red
    $results += "FAIL"
}

# Test order without SL blocked - should FAIL (throws exception as expected)
Write-Host "[5] Testing stop-loss required..." -NoNewline
$err = python -c "from forex_bot_platform.execution.mt5_executor import MT5DemoExecutor,SafetyConfig,OrderSide,SafetyCheckFailedError; e=MT5DemoExecutor(login='x',password='x',server='Demo',safety_config=SafetyConfig(require_stop_loss=True)); e.connect(); e.place_demo_order('EURUSD',OrderSide.BUY,0.1)" 2>&1
if ($err -match "Stop-loss required") {
    Write-Host "PASS" -ForegroundColor Green
    $results += "PASS"
} else {
    Write-Host "FAIL" -ForegroundColor Red
    $results += "FAIL"
}

# Test audit log
Write-Host "[6] Testing audit log..." -NoNewline
try {
    python -c "from forex_bot_platform.execution.mt5_executor import MT5DemoExecutor,SafetyConfig; e=MT5DemoExecutor(safety_config=SafetyConfig()); e.connect(); e._log_audit('test','details'); log=e.get_audit_log(); assert len(log)>0" 2>$null
    Write-Host "PASS" -ForegroundColor Green
    $results += "PASS"
} catch {
    Write-Host "FAIL" -ForegroundColor Red
    $results += "FAIL"
}

# Test rejection report
Write-Host "[7] Testing rejection report..." -NoNewline
try {
    python -c "from forex_bot_platform.execution.mt5_executor import MT5DemoExecutor,SafetyConfig,OrderSide; e=MT5DemoExecutor(safety_config=SafetyConfig()); e.connect(); e._record_rejection('EURUSD',OrderSide.BUY,0.1,'reason'); rep=e.get_rejection_report(); assert len(rep)>0" 2>$null
    Write-Host "PASS" -ForegroundColor Green
    $results += "PASS"
} catch {
    Write-Host "FAIL" -ForegroundColor Red
    $results += "FAIL"
}

Write-Host ""
Write-Host "Results:" $results -ForegroundColor Yellow
$pass = ($results | Where-Object { $_ -eq "PASS" }).Count
$total = $results.Count
if ($pass -eq $total) {
    Write-Host "All demo health checks passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "$pass/$total passed" -ForegroundColor Red
    exit 1
}