# Windows PowerShell launcher: creates the venv if missing, builds the model into a
# timestamped output\ subfolder (matching the launch.sh/launch.bat convention).
#
# Reads a repo-root .env file automatically (see .env.example) -- set REPORT=1 there to
# also run the full equity-research-report pipeline (Stages 1-6 -- see BLUEPRINT.md's
# "Equity Research Report pipeline" section) and produce a PDF alongside the Excel model,
# instead of passing it inline every run:
#   .\scripts\launch.ps1 unilever
# Reads TICKER/EXCHANGE from that instance's config.py; override via .env or
# $env:TICKER / $env:EXCHANGE if the config doesn't have them or you want a different pair.
# This makes several `claude -p` calls (subscription-billed, not separately metered --
# same convention as scripts/source_model.py) and takes noticeably longer than the
# Excel-only path.

param(
    [string]$Instance = "unilever"
)

$ErrorActionPreference = "Stop"

$ScriptsDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptsDir
$VenvDir = Join-Path $RootDir ".venv"
$ConfigSrc = Join-Path $RootDir "examples\$Instance\config.py"

# Load repo-root .env (git-ignored) into the process environment, if present. Blank lines
# and lines starting with # are skipped; existing $env: values (e.g. set inline before
# invoking this script) are left untouched rather than overridden.
$EnvFile = Join-Path $RootDir ".env"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        $line = $_.Trim()
        if ($line -eq "" -or $line.StartsWith("#")) { return }
        $parts = $line -split "=", 2
        if ($parts.Count -eq 2) {
            $key = $parts[0].Trim()
            $value = $parts[1].Trim()
            if (-not (Test-Path "Env:\$key")) {
                Set-Item -Path "Env:\$key" -Value $value
            }
        }
    }
}

$PythonExe = Join-Path $VenvDir "Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    Write-Output "No virtual environment found -- creating one at $VenvDir..."
    $SystemPython = Get-Command python -ErrorAction SilentlyContinue
    if (-not $SystemPython) {
        Write-Error "No python found on PATH."
        exit 1
    }
    & $SystemPython.Source -m venv $VenvDir
}

& $PythonExe -m pip install --quiet --upgrade pip
& $PythonExe -m pip install --quiet -r (Join-Path $ScriptsDir "requirements.txt")

$Timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$OutDir = Join-Path $RootDir "output\$Timestamp"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$env:OUTPUT_DIR = $OutDir

if ($env:REPORT -eq "1") {
    Write-Output "REPORT=1 -- running the full equity-report pipeline (Stages 1-6). This makes"
    Write-Output "several claude -p calls and can take a while -- it is not a quick command."
    $ReportArgs = @($Instance, "--output-dir", $OutDir)
    if ($env:TICKER) { $ReportArgs += @("--ticker", $env:TICKER) }
    if ($env:EXCHANGE) { $ReportArgs += @("--exchange", $env:EXCHANGE) }
    & $PythonExe (Join-Path $ScriptsDir "generate_equity_report.py") @ReportArgs
} else {
    & $PythonExe (Join-Path $ScriptsDir "build_unilever_model.py") --instance $Instance
}

Copy-Item $ConfigSrc -Destination $OutDir
Write-Output "Outputs written to: $OutDir"
