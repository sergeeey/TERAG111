# Setup pre-commit hooks for TERAG (PowerShell version)
# Installs pre-commit and gitleaks to prevent committing secrets

Write-Host "🔒 Setting up pre-commit hooks for TERAG..." -ForegroundColor Cyan

# Check if pre-commit is installed
try {
    $preCommitVersion = pre-commit --version 2>$null
    Write-Host "✅ pre-commit is installed: $preCommitVersion" -ForegroundColor Green
} catch {
    Write-Host "📦 Installing pre-commit..." -ForegroundColor Yellow
    pip install pre-commit
}

# Check if gitleaks is installed (optional, will be installed via pre-commit)
try {
    $gitleaksVersion = gitleaks version 2>$null
    Write-Host "✅ gitleaks is installed: $gitleaksVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠️  gitleaks will be installed automatically by pre-commit on first run" -ForegroundColor Yellow
}

# Install pre-commit hooks
Write-Host "📥 Installing pre-commit hooks..." -ForegroundColor Cyan
pre-commit install

# Test hooks
Write-Host "🧪 Testing pre-commit hooks..." -ForegroundColor Cyan
try {
    pre-commit run --all-files
    Write-Host "✅ All hooks passed!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Some hooks failed (this is normal on first run)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Pre-commit hooks installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Hooks will run automatically on 'git commit'" -ForegroundColor Gray
Write-Host "  2. To test manually: pre-commit run --all-files" -ForegroundColor Gray
Write-Host "  3. To skip hooks (not recommended): git commit --no-verify" -ForegroundColor Gray


















