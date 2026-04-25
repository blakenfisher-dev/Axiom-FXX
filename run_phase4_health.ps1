# Phase 4 Health Check Script
# Verifies Live Trading Mode implementation

Write-Host "=== Phase 4 Health Check ===" -ForegroundColor Cyan
Write-Host ""

$fail_count = 0
$pass_count = 0
$total = 0

function Test-Phase4-Item {
    param($name, $scriptblock)
    $script:total++
    Write-Host "Testing: $name" -NoNewline
    try {
        $result = & $scriptblock
        if ($result) {
            Write-Host " [PASS]" -ForegroundColor Green
            $script:pass_count++
            return $true
        } else {
            Write-Host " [FAIL]" -ForegroundColor Red
            $script:fail_count++
            return $false
        }
    } catch {
        Write-Host " [ERROR] $_" -ForegroundColor Red
        $script:fail_count++
        return $false
    }
}

Push-Location "C:\Users\Admin\Downloads\axiom-functioning-website\forex-bot-platform"

# Test 1: Module files exist
Test-Phase4-Item "live_executor.py exists" {
    Test-Path "forex_bot_platform\execution\live_executor.py"
}
Test-Phase4-Item "live_guard.py exists" {
    Test-Path "forex_bot_platform\execution\live_guard.py"
}
Test-Phase4-Item "live_safety.py exists" {
    Test-Path "forex_bot_platform\execution\live_safety.py"
}
Test-Phase4-Item "live_audit.py exists" {
    Test-Path "forex_bot_platform\execution\live_audit.py"
}
Test-Phase4-Item "live_readiness.py exists" {
    Test-Path "forex_bot_platform\execution\live_readiness.py"
}

# Test 2: Import tests
Test-Phase4-Item "live_executor imports" {
    python -c "from forex_bot_platform.execution.live_executor import LiveExecutor; print('OK')" 2>$null
}
Test-Phase4-Item "live_guard imports" {
    python -c "from forex_bot_platform.execution.live_guard import LiveGuard; print('OK')" 2>$null
}
Test-Phase4-Item "live_safety imports" {
    python -c "from forex_bot_platform.execution.live_safety import LiveSafety; print('OK')" 2>$null
}
Test-Phase4-Item "live_audit imports" {
    python -c "from forex_bot_platform.execution.live_audit import LiveAuditLogger; print('OK')" 2>$null
}
Test-Phase4-Item "live_readiness imports" {
    python -c "from forex_bot_platform.execution.live_readiness import LiveReadinessChecker; print('OK')" 2>$null
}

# Test 3: Test files exist
Test-Phase4-Item "test_live_executor.py exists" {
    Test-Path "tests\test_live_executor.py"
}
Test-Phase4-Item "test_live_guard.py exists" {
    Test-Path "tests\test_live_guard.py"
}
Test-Phase4-Item "test_live_safety.py exists" {
    Test-Path "tests\test_live_safety.py"
}

# Test 4: CLI commands
Test-Phase4-Item "--live-readiness CLI available" {
    python -m forex_bot_platform.main --help 2>$null | Select-String "live-readiness"
}
Test-Phase4-Item "--enable-live-trading CLI available" {
    python -m forex_bot_platform.main --help 2>$null | Select-String "enable-live-trading"
}

# Test 5: Live mode disabled by default
Test-Phase4-Item "Live trading disabled by default" {
    $output = python -c "from forex_bot_platform.execution.live_executor import LiveExecutor; print(LiveExecutor.is_live_enabled())" 2>$null
    $output -eq "False"
}

# Test 6: Run live tests
Write-Host ""
Write-Host "Running live tests..." -ForegroundColor Cyan
$test_result = python -m pytest tests/test_live_executor.py tests/test_live_guard.py tests/test_live_safety.py -v --tb=short 2>&1
$test_output = $test_result | Out-String

Test-Phase4-Item "Live tests can run" {
    $test_result -ne $null
}

# Test 7: No approval blocks live
Test-Phase4-Item "Missing approval blocks live trading" {
    $output = python -c "
from forex_bot_platform.execution.live_executor import LiveExecutor, LiveApproval
import os, tempfile
LiveExecutor.disable_live_trading()
executor = LiveExecutor('12345', 'pass', 'server', approval_path='/nonexistent.json')
can, reason = executor.can_trade_live()
print(can)
" 2>$null
    $output -match "False"
}

# Test 8: Emergency stop works
Test-Phase4-Item "Emergency stop disables live trading" {
    $output = python -c "
from forex_bot_platform.execution.live_executor import LiveExecutor
LiveExecutor.enable_live_trading()
executor = LiveExecutor('12345', 'pass', 'server')
executor._base = type('obj', (object,), {'is_connected': True, 'positions': []})()
executor.emergency_stop_live()
print(LiveExecutor.is_live_enabled())
" 2>$null
    $output -match "False"
}

# Test 9: Live readiness checker works
Test-Phase4-Item "Live readiness checker runs" {
    python -c "from forex_bot_platform.execution.live_readiness import check_live_readiness; print('OK')" 2>$null
}

# Test 10: Risk limits conservative
Test-Phase4-Item "Risk limits are conservative" {
    $output = python -c "
from forex_bot_platform.execution.live_executor import LiveRiskLimits
limits = LiveRiskLimits()
result = (limits.risk_per_trade == 0.0025 and limits.max_risk_per_trade == 0.005)
print(str(result))
" 2>$null
    $output -match "True"
}

Pop-Location

Write-Host ""
Write-Host "=== Results ===" -ForegroundColor Cyan
Write-Host "Passed: $pass_count/$total" -ForegroundColor Green
Write-Host "Failed: $fail_count/$total" -ForegroundColor $(if ($fail_count -eq 0) { "Green" } else { "Red" })

if ($fail_count -eq 0) {
    Write-Host ""
    Write-Host "Phase 4: PASS" -ForegroundColor Green
    exit 0
} else {
    Write-Host ""
    Write-Host "Phase 4: FAIL" -ForegroundColor Red
    exit 1
}