#!/usr/bin/env bash
# Unix/macOS/Linux launcher: creates the venv if missing, activates it, builds the model
# into a timestamped output/ subfolder (matching the colossal-visuals convention).
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

python "$SCRIPTS_DIR/build_bank_model.py" --bank "$BANK"

cp "$CONFIG_SRC" "$OUT_DIR/"
echo "Outputs written to: $OUT_DIR"
