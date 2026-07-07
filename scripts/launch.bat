@echo off
REM Windows launcher: creates the venv if missing, activates it, builds the model into a
REM timestamped output\ subfolder (matching the colossal-visuals convention).
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

python "%SCRIPTS_DIR%build_bank_model.py" --bank "%BANK%"

copy "%CONFIG_SRC%" "%OUT_DIR%\" >nul
echo Outputs written to: %OUT_DIR%

endlocal
