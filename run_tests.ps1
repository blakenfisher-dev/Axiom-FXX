# Run All Tests Script

Write-Host "Running All Tests..." -ForegroundColor Cyan
Write-Host ""

python -m pytest -q

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "All tests PASSED!" -ForegroundColor Green
    exit 0
} else {
    Write-Host ""
    Write-Host "Some tests FAILED!" -ForegroundColor Red
    exit 1
}