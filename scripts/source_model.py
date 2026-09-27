"""Model-sourcing pipeline stage (Stage 0 of the equity-report pipeline): given an
institution, verifies/refreshes examples/<institution>/config.py + research_output.md
against its real disclosed figures. See bizplan/report/sourcing.py for the actual logic.

    python scripts/source_model.py <institution> [hint-url ...]

Requires the `claude` CLI on PATH, authenticated via `claude login` (subscription) —
do not add --bare, which forces raw-API-key billing instead.
"""
import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from bizplan.report.sourcing import source_model  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("institution", help="Institution folder name, e.g. 'unilever'")
    parser.add_argument("hints", nargs="*", help="Optional starting URLs")
    args = parser.parse_args()
    source_model(args.institution, args.hints)


if __name__ == "__main__":
    main()
