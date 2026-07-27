#!/usr/bin/env bash
# Unix/macOS/Linux launcher: creates the venv if missing, activates it, builds the model
# into a timestamped output/ subfolder (matching the colossal-visuals convention).
#
# Set REPORT=1 to also run the full equity-research-report pipeline (Stages 1-6 -- see
# BLUEPRINT.md's "Equity Research Report pipeline" section) and produce a PDF alongside
# the Excel model, e.g.:
#   REPORT=1 ./scripts/launch.sh family_bank_kenya
# Reads TICKER/EXCHANGE from that institution's config.py; override with env vars
# (TICKER=... EXCHANGE=...) if the config doesn't have them or you want a different pair.
# This makes several `claude -p` calls (subscription-billed, not separately metered --
# same convention as scripts/source_model.py) and takes noticeably longer than the
# Excel-only path.
set -e

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPTS_DIR")"
VENV_DIR="$ROOT_DIR/.venv"
BANK="${1:-family_bank_kenya}"
CONFIG_SRC="$ROOT_DIR/examples/$BANK/config.py"

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
    python "$SCRIPTS_DIR/generate_equity_report.py" "$BANK" --output-dir "$OUT_DIR" "${TICKER_ARGS[@]}"
else
    python "$SCRIPTS_DIR/build_bank_model.py" --bank "$BANK"
fi

cp "$CONFIG_SRC" "$OUT_DIR/"
echo "Outputs written to: $OUT_DIR"
