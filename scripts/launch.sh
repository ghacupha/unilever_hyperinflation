#!/usr/bin/env bash
# Unix/macOS/Linux launcher: creates the venv if missing, activates it, builds the model
# into a timestamped output/ subfolder (matching the colossal-visuals convention).
#
# Reads a repo-root .env file automatically (see .env.example) -- set REPORT=1 there to
# also run the full equity-research-report pipeline (Stages 1-6 -- see BLUEPRINT.md's
# "Equity Research Report pipeline" section) and produce a PDF alongside the Excel model,
# instead of passing it inline every run. Inline still works too:
#   REPORT=1 ./scripts/launch.sh acorn_i_reit
# NOTE: the REPORT=1 pipeline (bizplan/report/*) still imports the retired bank_calculations/
# bank_excel_renderer modules and will not currently run -- REIT adaptation is tracked as a
# follow-up in BACKLOG.md. The default (Excel-only) path below works.
# Reads TICKER/EXCHANGE from that REIT's config.py; override via .env or inline
# env vars (TICKER=... EXCHANGE=...) if the config doesn't have them or you want a
# different pair.
# This makes several `claude -p` calls (subscription-billed, not separately metered --
# same convention as scripts/source_model.py) and takes noticeably longer than the
# Excel-only path.
set -e

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPTS_DIR")"
VENV_DIR="$ROOT_DIR/.venv"
REIT="${1:-acorn_i_reit}"
CONFIG_SRC="$ROOT_DIR/examples/$REIT/config.py"

# Load repo-root .env (git-ignored, see .env.example) into the environment, if present --
# lets REPORT=1/TICKER/EXCHANGE be set once instead of inline every run.
# A variable already exported by the calling shell (e.g. REPORT=0 ./launch.sh) wins over
# the .env file's value, matching standard dotenv precedence.
if [ -f "$ROOT_DIR/.env" ]; then
    while IFS='=' read -r key value; do
        [ -z "$key" ] && continue
        case "$key" in \#*) continue ;; esac
        if [ -z "${!key+x}" ]; then
            export "$key=$value"
        fi
    done < "$ROOT_DIR/.env"
fi

if [ ! -f "$VENV_DIR/bin/python" ]; then
    echo "No virtual environment found — creating one at $VENV_DIR..."
    PYTHON_BIN="$(command -v python3 || command -v python)"
    if [ -z "$PYTHON_BIN" ]; then
        echo "No python3/python found on PATH." >&2
        exit 1
    fi
    "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r "$SCRIPTS_DIR/requirements.txt"

TIMESTAMP="$(date +%Y-%m-%d_%H%M%S)"
OUT_DIR="$ROOT_DIR/output/$TIMESTAMP"
mkdir -p "$OUT_DIR"
export OUTPUT_DIR="$OUT_DIR"

if [ "$REPORT" = "1" ]; then
    echo "REPORT=1 -- running the full equity-report pipeline (Stages 1-6). This makes"
    echo "several claude -p calls and can take a while -- it is not a quick command."
    TICKER_ARGS=()
    [ -n "$TICKER" ] && TICKER_ARGS+=(--ticker "$TICKER")
    [ -n "$EXCHANGE" ] && TICKER_ARGS+=(--exchange "$EXCHANGE")
    python "$SCRIPTS_DIR/generate_equity_report.py" "$REIT" --output-dir "$OUT_DIR" "${TICKER_ARGS[@]}"
else
    python "$SCRIPTS_DIR/build_reit_model.py" --reit "$REIT"
fi

cp "$CONFIG_SRC" "$OUT_DIR/"
echo "Outputs written to: $OUT_DIR"
