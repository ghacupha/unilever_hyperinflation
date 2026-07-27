@echo off
REM Windows launcher: creates the venv if missing, activates it, builds the model into a
REM timestamped output\ subfolder (matching the colossal-visuals convention).
REM
REM Set REPORT=1 to also run the full equity-research-report pipeline (Stages 1-6 -- see
REM BLUEPRINT.md's "Equity Research Report pipeline" section) and produce a PDF alongside
REM the Excel model, e.g.:
REM   set REPORT=1 & scripts\launch.bat family_bank_kenya
REM Reads TICKER/EXCHANGE from that institution's config.py; override with
REM set TICKER=... & set EXCHANGE=... if the config doesn't have them.
REM This makes several `claude -p` calls (subscription-billed, not separately metered)
REM and takes noticeably longer than the Excel-only path.
setlocal

set "SCRIPTS_DIR=%~dp0"
for %%I in ("%SCRIPTS_DIR%\..") do set "ROOT_DIR=%%~fI"
set "VENV_DIR=%ROOT_DIR%\.venv"
set "BANK=%~1"
if "%BANK%"=="" set "BANK=family_bank_kenya"
set "CONFIG_SRC=%ROOT_DIR%\examples\%BANK%\config.py"

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo No virtual environment found — creating one at %VENV_DIR%...
    where python >nul 2>nul
    if errorlevel 1 (
        echo No python found on PATH.
        exit /b 1
    )
    python -m venv "%VENV_DIR%"
)

call "%VENV_DIR%\Scripts\activate.bat"

python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r "%SCRIPTS_DIR%requirements.txt"

REM Native batch date/time parsing is locale-fragile, so use PowerShell for a reliable
REM sortable timestamp.
for /f %%T in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HHmmss"') do set "TIMESTAMP=%%T"
set "OUT_DIR=%ROOT_DIR%\output\%TIMESTAMP%"
mkdir "%OUT_DIR%"
set "OUTPUT_DIR=%OUT_DIR%"

if "%REPORT%"=="1" (
    echo REPORT=1 -- running the full equity-report pipeline ^(Stages 1-6^). This makes
    echo several claude -p calls and can take a while -- it is not a quick command.
    set "TICKER_ARG="
    set "EXCHANGE_ARG="
    if not "%TICKER%"=="" set "TICKER_ARG=--ticker %TICKER%"
    if not "%EXCHANGE%"=="" set "EXCHANGE_ARG=--exchange %EXCHANGE%"
    python "%SCRIPTS_DIR%generate_equity_report.py" "%BANK%" --output-dir "%OUT_DIR%" %TICKER_ARG% %EXCHANGE_ARG%
) else (
    python "%SCRIPTS_DIR%build_bank_model.py" --bank "%BANK%"
)

copy "%CONFIG_SRC%" "%OUT_DIR%\" >nul
echo Outputs written to: %OUT_DIR%

endlocal
