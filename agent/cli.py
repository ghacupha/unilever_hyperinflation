"""Entry point for the institution onboarding/update agent.

    python agent/cli.py onboard <institution> [hint-url ...]
    python agent/cli.py update <institution>

Requires ANTHROPIC_KEY (set it in the repo-root .env — real API cost per run,
this calls the Anthropic API directly with web search + PDF reading). Never
touches bizplan/financial/{bank_calculations,bank_excel_renderer}.py — only
creates/updates examples/<institution>/ files, per the SOP in
.devops/agents/bank-onboarding.md.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from agent import build_runner, config_writer, manifest, research  # noqa: E402
from bizplan.config_loader import REQUIRED_FIELDS  # noqa: E402


def _anthropic_client() -> anthropic.Anthropic:
    """Loads the repo-root .env and builds the client explicitly off
    ANTHROPIC_KEY — the Anthropic SDK's own auto-detection only looks for
    ANTHROPIC_API_KEY/ANTHROPIC_AUTH_TOKEN, not this repo's chosen variable
    name, so it has to be wired through by hand."""
    load_dotenv(REPO_ROOT / ".env")
    key = os.environ.get("ANTHROPIC_KEY")
    if not key:
        raise RuntimeError(
            "ANTHROPIC_KEY is not set. Add it to the repo-root .env file "
            "(see .env's ANTHROPIC_KEY= placeholder) before running the agent."
        )
    return anthropic.Anthropic(api_key=key)

SOP_PATH = REPO_ROOT / ".devops" / "agents" / "bank-onboarding.md"
TEMPLATE_CONFIG_PATH = REPO_ROOT / "examples" / "family_bank_kenya" / "config.py"
TEMPLATE_RESEARCH_PATH = REPO_ROOT / "examples" / "family_bank_kenya" / "research_output.md"


def _onboarding_prompt(institution: str, hints: list[str]) -> str:
    sop = SOP_PATH.read_text(encoding="utf-8")
    hint_text = "\n".join(f"- {h}" for h in hints) if hints else "(none given — search for them)"
    return (
        f"Follow the SOP below to onboard a new bank/financial institution called "
        f"'{institution}' into this repo's financial model generator.\n\n{sop}\n\n"
        f"Starting points for finding this institution's filings (may be empty):\n{hint_text}\n\n"
        f"Locate its most recent annual report (and, if findable, a prior year for "
        f"comparison) and download the PDFs with the download_file tool into the data "
        f"directory. Stop once you have enough source documents to populate the config.py "
        f"schema — you do not need every possible document."
    )


def _extraction_prompt(institution: str) -> str:
    template_config = TEMPLATE_CONFIG_PATH.read_text(encoding="utf-8")
    template_research = TEMPLATE_RESEARCH_PATH.read_text(encoding="utf-8")
    return (
        f"You've been given {institution}'s annual report filing(s) as attached documents. "
        f"Extract the facts needed to populate this repo's config.py schema, then produce "
        f"exactly two fenced code blocks in your response:\n\n"
        f"1. A ```python fenced block containing a complete config.py module body for "
        f"'{institution}', structured exactly like this worked example for Family Bank "
        f"Kenya (same section headers, same field names, same REQUIRED_FIELDS: "
        f"{', '.join(REQUIRED_FIELDS)}):\n\n```python\n{template_config}\n```\n\n"
        f"2. A ```markdown fenced block containing a research_output.md body for "
        f"'{institution}', with a source/accessed field per datapoint, structured like "
        f"this worked example:\n\n```markdown\n{template_research[:8000]}\n```\n\n"
        f"Use real figures from the attached documents only — never fabricate. Where a "
        f"figure genuinely isn't disclosed, use a clearly-marked placeholder and note it "
        f"in the research doc rather than inventing a number. Keep off-balance-sheet "
        f"exposure as its own line/section, never folded into on-balance-sheet loan "
        f"tables, since this institution's disclosure convention may differ from the "
        f"worked example's."
    )


def onboard(institution: str, hints: list[str]) -> None:
    client = _anthropic_client()
    institution_dir = REPO_ROOT / "examples" / institution
    data_dir = REPO_ROOT / "data" / institution
    institution_dir.mkdir(parents=True, exist_ok=True)

    pdf_paths = research.locate_and_download_filings(
        client, _onboarding_prompt(institution, hints), data_dir)
    if not pdf_paths:
        raise RuntimeError("No filings were downloaded — cannot proceed without source documents.")

    response_text = research.extract_facts(client, pdf_paths, _extraction_prompt(institution))
    config_source, research_source = research.parse_artifacts(response_text)

    config_writer.write_config(institution_dir, config_source)  # raises on schema failure
    (institution_dir / "research_output.md").write_text(research_source, encoding="utf-8")

    m = manifest.load(institution_dir)
    for pdf_path in pdf_paths:
        manifest.record_source(m, url="", local_path=pdf_path, period="onboarding")
    manifest.save(institution_dir, m)

    result = build_runner.run_build(institution)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"Build failed for {institution} — see output above.")
    print(f"Onboarded {institution}. Model built successfully. Final Master Check "
          f"confirmation still needs a real Excel open (no LibreOffice here to "
          f"auto-recalculate — same known limitation as the rest of this repo).")


def update(institution: str) -> None:
    client = _anthropic_client()
    institution_dir = REPO_ROOT / "examples" / institution
    data_dir = REPO_ROOT / "data" / institution
    if not institution_dir.exists():
        raise RuntimeError(f"{institution} hasn't been onboarded yet — run 'onboard' first.")

    m = manifest.load(institution_dir)
    existing_config = (institution_dir / "config.py").read_text(encoding="utf-8")
    existing_research = (institution_dir / "research_output.md").read_text(encoding="utf-8")

    search_prompt = (
        f"Check whether '{institution}' has published a newer annual or quarterly filing "
        f"than what's already been ingested. If nothing newer exists, say so and stop — "
        f"do not re-download what's already here.\n\n"
        f"Already-ingested sources:\n{m['sources']}\n\n"
        f"If a newer filing exists, download it with download_file."
    )
    pdf_paths = research.locate_and_download_filings(client, search_prompt, data_dir)
    if not pdf_paths:
        print(f"No newer filing found for {institution}. Nothing to update.")
        return

    extraction_prompt = (
        f"You've been given {institution}'s newly-published filing as an attached document, "
        f"plus its existing config.py and research_output.md below for context. Produce an "
        f"UPDATED config.py and research_output.md as two fenced code blocks "
        f"(```python and ```markdown), mechanically rolling the config forward per this "
        f"repo's established convention: move the value that was the nearest projected "
        f"year into ACTUALS/ACTUAL_YEARS now that a real figure exists for it, and extend "
        f"YEARS by one more forward year to hold the projection horizon constant. Preserve "
        f"every other field as-is — this is a roll-forward, not a rewrite. Append the new "
        f"filing's sources to the research doc rather than replacing prior entries.\n\n"
        f"Existing config.py:\n```python\n{existing_config}\n```\n\n"
        f"Existing research_output.md:\n```markdown\n{existing_research}\n```"
    )
    response_text = research.extract_facts(client, pdf_paths, extraction_prompt)
    config_source, research_source = research.parse_artifacts(response_text)

    config_writer.write_config(institution_dir, config_source)
    (institution_dir / "research_output.md").write_text(research_source, encoding="utf-8")

    for pdf_path in pdf_paths:
        manifest.record_source(m, url="", local_path=pdf_path, period="update")
    manifest.save(institution_dir, m)

    result = build_runner.run_build(institution)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"Build failed for {institution} — see output above.")
    print(f"Updated {institution}. Model rebuilt successfully.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bank model onboarding/update agent")
    sub = parser.add_subparsers(dest="command", required=True)

    onboard_p = sub.add_parser("onboard", help="Research and onboard a new institution")
    onboard_p.add_argument("institution", help="Institution folder name, e.g. 'equity_bank_kenya'")
    onboard_p.add_argument("hints", nargs="*", help="Optional starting URLs (investor relations page, etc.)")

    update_p = sub.add_parser("update", help="Check for and ingest new filings for an existing institution")
    update_p.add_argument("institution")

    args = parser.parse_args()
    if args.command == "onboard":
        onboard(args.institution, args.hints)
    elif args.command == "update":
        update(args.institution)


if __name__ == "__main__":
    main()
