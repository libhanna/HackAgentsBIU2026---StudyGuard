# =====================================================================
#  StudyGuard - Run-all launcher
#  Opens 4 separate PowerShell windows, one per component, in this order:
#    1. MCP server   (src/agent_skeleton/server.py)
#    2. Agent        (src/agent_skeleton/agent.py)
#    3. Flask API    (app.py)
#    4. Vue UI       (src/ui  -  npm run dev)
#
#  Usage:
#    Right-click  ->  Run with PowerShell
#  or from a PowerShell prompt:
#    powershell -ExecutionPolicy Bypass -File .\run-all.ps1
#
#  NOTE:
#  The MCP "server" terminal is informational only - agent.py spawns its
#  own internal server.py over stdio. The standalone window is useful for
#  seeing import / startup errors directly.
# =====================================================================

$ErrorActionPreference = "Stop"

# Project root = the directory this script sits in
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ProjectRoot

Write-Host "Project root: $ProjectRoot" -ForegroundColor Cyan

# --- Pick a python executable (prefer local venv if present) ----------
$Python = "python"
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (Test-Path $VenvPython) {
    $Python = $VenvPython
    Write-Host "Using venv python: $Python" -ForegroundColor Green
} else {
    Write-Host "Using system python (no .venv found)" -ForegroundColor Yellow
}

# Make sure src/ is on PYTHONPATH so `import agent_skeleton...` works
$env:PYTHONPATH = "$ProjectRoot\src;$ProjectRoot;$env:PYTHONPATH"

# Helper: open a new PowerShell window that cd-s to a folder and runs a command
function Start-InNewWindow {
    param(
        [string]$Title,
        [string]$WorkDir,
        [string]$Command
    )

    # -NoExit  -> keep window open so we can read logs / errors
    $psArgs = @(
        "-NoExit",
        "-ExecutionPolicy", "Bypass",
        "-Command",
        "`$Host.UI.RawUI.WindowTitle = '$Title'; " +
        "Set-Location '$WorkDir'; " +
        "`$env:PYTHONPATH = '$ProjectRoot\src;$ProjectRoot;' + `$env:PYTHONPATH; " +
        "$Command"
    )

    Start-Process -FilePath "powershell.exe" -ArgumentList $psArgs | Out-Null
    Write-Host "  -> launched [$Title]" -ForegroundColor Green
}

# 1. MCP server
Write-Host "[1/4] Starting MCP server..." -ForegroundColor Cyan
Start-InNewWindow `
    -Title  "StudyGuard | MCP server" `
    -WorkDir $ProjectRoot `
    -Command "& '$Python' src\agent_skeleton\server.py"
Start-Sleep -Seconds 2

# 2. Agent
Write-Host "[2/4] Starting Agent..." -ForegroundColor Cyan
Start-InNewWindow `
    -Title  "StudyGuard | Agent" `
    -WorkDir $ProjectRoot `
    -Command "& '$Python' src\agent_skeleton\agent.py"
Start-Sleep -Seconds 2

# 3. Flask app
Write-Host "[3/4] Starting Flask app (app.py)..." -ForegroundColor Cyan
Start-InNewWindow `
    -Title  "StudyGuard | Flask app" `
    -WorkDir $ProjectRoot `
    -Command "& '$Python' app.py"
Start-Sleep -Seconds 2

# 4. UI
Write-Host "[4/4] Starting UI (npm run dev)..." -ForegroundColor Cyan
$UiDir = Join-Path $ProjectRoot "src\ui"
if (-not (Test-Path (Join-Path $UiDir "node_modules"))) {
    Write-Host "  -> node_modules not found, running 'npm install' first..." -ForegroundColor Yellow
    Start-InNewWindow `
        -Title  "StudyGuard | UI" `
        -WorkDir $UiDir `
        -Command "npm install ; npm run dev"
} else {
    Start-InNewWindow `
        -Title  "StudyGuard | UI" `
        -WorkDir $UiDir `
        -Command "npm run dev"
}

Write-Host ""
Write-Host "All 4 components launched in separate windows." -ForegroundColor Green
Write-Host "UI should be reachable at: http://localhost:5173" -ForegroundColor Cyan
Write-Host "Flask API at:              http://localhost:5000" -ForegroundColor Cyan
