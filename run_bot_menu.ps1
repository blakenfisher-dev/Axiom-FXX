# Forex Bot Platform - Main Menu
# Run this from PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Forex Bot Platform - Menu" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

function Show-Menu {
    Write-Host "Choose an option:" -ForegroundColor Yellow
    Write-Host "1. Run Backtest" 
    Write-Host "2. Run Strategy Comparison"
    Write-Host "3. Run Demo Dry Run"
    Write-Host "4. Run Demo Soak Test"
    Write-Host "5. Run Live Readiness Check"
    Write-Host "6. Launch Streamlit Dashboard"
    Write-Host "7. Run All Tests"
    Write-Host "8. Emergency Stop Live Trading"
    Write-Host "9. Exit"
    Write-Host ""
}

$exit = $false

while (-not $exit) {
    Show-Menu
    
    $choice = Read-Host "Enter choice (1-9)"
    
    switch ($choice) {
        "1" {
            Write-Host "Running Backtest..." -ForegroundColor Green
            $pair = Read-Host "Enter pair (default: EURUSD)"
            $strategy = Read-Host "Enter strategy (default: Breakout)"
            $timeframe = Read-Host "Enter timeframe (default: 1h)"
            
            python -m forex_bot_platform.main --pair ($pair -or "EURUSD") --strategy ($strategy -or "Breakout") --timeframe ($timeframe -or "1h")
        }
        "2" {
            Write-Host "Running Strategy Comparison..." -ForegroundColor Green
            python -m forex_bot_platform.research_engine.experiment_runner --pair EURUSD --timeframe 1h --experiments 50
        }
        "3" {
            Write-Host "Running Demo Dry Run..." -ForegroundColor Green
            $login = Read-Host "Enter MT5 login"
            $server = Read-Host "Enter server (default: MetaQuotes-Demo)"
            
            python -m forex_bot_platform.main --demo-dry-run --login $login --server ($server -or "MetaQuotes-Demo")
        }
        "4" {
            Write-Host "Running Demo Soak Test..." -ForegroundColor Green
            $login = Read-Host "Enter MT5 login"
            $server = Read-Host "Enter server (default: MetaQuotes-Demo)"
            
            python -m forex_bot_platform.main --demo-soak --login $login --server ($server -or "MetaQuotes-Demo")
        }
        "5" {
            Write-Host "Running Live Readiness Check..." -ForegroundColor Green
            python -m forex_bot_platform.main --live-readiness
        }
        "6" {
            Write-Host "Launching Dashboard..." -ForegroundColor Green
            streamlit run forex_bot_platform/dashboard/app.py
        }
        "7" {
            Write-Host "Running All Tests..." -ForegroundColor Green
            python -m pytest -q
            if ($LASTEXITCODE -eq 0) {
                Write-Host "All tests PASSED!" -ForegroundColor Green
            } else {
                Write-Host "Some tests FAILED!" -ForegroundColor Red
            }
        }
        "8" {
            Write-Host "EMERGENCY STOP!" -ForegroundColor Red
            $confirm = Read-Host "Type 'YES' to confirm emergency stop"
            if ($confirm -eq "YES") {
                python -m forex_bot_platform.main --emergency-stop-live
                Write-Host "Live trading has been DISABLED" -ForegroundColor Red
            }
        }
        "9" {
            Write-Host "Exiting..." -ForegroundColor Yellow
            $exit = $true
        }
        default {
            Write-Host "Invalid choice" -ForegroundColor Red
        }
    }
    
    if (-not $exit) {
        Write-Host ""
        Write-Host "Press Enter to continue..."
        Read-Host
        Clear-Host
    }
}

Write-Host "Goodbye!" -ForegroundColor Cyan