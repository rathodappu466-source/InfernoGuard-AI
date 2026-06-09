# ════════════════════════════════════════════════════════════════════════════════
# InfernoGuard AI — Cleanup Script
# ════════════════════════════════════════════════════════════════════════════════
# This script removes unnecessary files and folders from your project.
# Run this ONCE to clean up your project before deploying or committing to Git.
#
# Usage: .\CLEANUP_SCRIPT.ps1
# ════════════════════════════════════════════════════════════════════════════════

Write-Host "🔥 InfernoGuard AI — Project Cleanup Script" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ── Stop all Python processes ──────────────────────────────────────────────────
Write-Host "🛑 Step 1: Stopping all Python processes..." -ForegroundColor Yellow
try {
    Get-Process python -ErrorAction Stop | Stop-Process -Force
    Write-Host "   ✅ Python processes stopped" -ForegroundColor Green
} catch {
    Write-Host "   ℹ️  No Python processes running" -ForegroundColor Gray
}
Write-Host ""

# ── Delete infernoguard_ai folder ──────────────────────────────────────────────
Write-Host "🗑️  Step 2: Deleting infernoguard_ai folder (venv + duplicates)..." -ForegroundColor Yellow
if (Test-Path "infernoguard_ai") {
    Remove-Item "infernoguard_ai" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "   ✅ infernoguard_ai folder deleted" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  infernoguard_ai folder not found (already deleted)" -ForegroundColor Gray
}
Write-Host ""

# ── Delete __pycache__ folders ─────────────────────────────────────────────────
Write-Host "🗑️  Step 3: Deleting __pycache__ folders..." -ForegroundColor Yellow
$pycacheFolders = Get-ChildItem -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue
$count = ($pycacheFolders | Measure-Object).Count
if ($count -gt 0) {
    $pycacheFolders | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "   ✅ $count __pycache__ folders deleted" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  No __pycache__ folders found" -ForegroundColor Gray
}
Write-Host ""

# ── Delete log files ───────────────────────────────────────────────────────────
Write-Host "🗑️  Step 4: Deleting log files..." -ForegroundColor Yellow
$logFiles = Get-ChildItem -Filter "*.log" -ErrorAction SilentlyContinue
$logCount = ($logFiles | Measure-Object).Count
if ($logCount -gt 0) {
    $logFiles | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host "   ✅ $logCount log file(s) deleted" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  No log files found" -ForegroundColor Gray
}
Write-Host ""

# ── Optional: Clean old screenshots ────────────────────────────────────────────
Write-Host "📸 Step 5: Screenshot cleanup (optional)..." -ForegroundColor Yellow
if (Test-Path "screenshots") {
    $screenshotCount = (Get-ChildItem "screenshots" -Filter "*.jpg" -ErrorAction SilentlyContinue | Measure-Object).Count
    Write-Host "   ℹ️  Found $screenshotCount screenshot(s)" -ForegroundColor Gray
    Write-Host "   ℹ️  Skipping (you may want to keep these for testing)" -ForegroundColor Gray
    Write-Host "   ℹ️  To delete: Remove-Item 'screenshots\*.jpg' -Force" -ForegroundColor Gray
} else {
    Write-Host "   ℹ️  screenshots folder not found" -ForegroundColor Gray
}
Write-Host ""

# ── Summary ────────────────────────────────────────────────────────────────────
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "   ✅ Python processes stopped" -ForegroundColor Green
Write-Host "   ✅ infernoguard_ai folder deleted" -ForegroundColor Green
Write-Host "   ✅ __pycache__ folders cleaned" -ForegroundColor Green
Write-Host "   ✅ Log files removed" -ForegroundColor Green
Write-Host "   ℹ️  Screenshots preserved" -ForegroundColor Gray
Write-Host ""
Write-Host "🚀 Your project is now clean and ready!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Read PROJECT_HEALTH_REPORT.md for full analysis" -ForegroundColor White
Write-Host "   2. Read QUICK_START.md to run the application" -ForegroundColor White
Write-Host "   3. Run: streamlit run app.py" -ForegroundColor Yellow
Write-Host ""
