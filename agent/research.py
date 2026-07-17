"""Standalone research step: locates a bank's public filings, downloads them,
and extracts the facts needed to populate this repo's config.py schema.

Calls the Anthropic API directly with a manual tool-use loop (server-side
`web_search_20260209` tool + a custom `download_file` tool) to locate and
fetch filings, then feeds the downloaded PDFs back to Claude as native
`document` content blocks for extraction — no local text-extraction step
unless a PDF fails to parse via the API, in which case this falls back to
the pypdf/pdfplumber/pikepdf/pymupdf recovery toolchain already proven in
this repo (see BACKLOG.md's Phase -0.5: 4 of 8 source PDFs were found
malformed on disk for Family Bank Kenya and needed exactly this recovery
path).
"""
from __future__ import annotations

import base64
import re
from pathlib import Path

import anthropic
import httpx

MODEL = "claude-opus-4-8"
MAX_TOKENS = 16000
MAX_TOOL_ITERATIONS = 30  # hard cap so a confused research loop can't run forever

DOWNLOAD_TOOL = {
    "type": "custom",
    "name": "download_file",
    "description": (
        "Download a file (annual report, prospectus, or other filing PDF) from a "
        "URL to local disk. Use this once web_search has located a specific filing."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Direct URL to the PDF"},
            "filename": {"type": "string", "description": "Filename to save as, e.g. 'annual-report-2026.pdf'"},
        },
        "required": ["url", "filename"],
    },
}
WEB_SEARCH_TOOL = {"type": "web_search_20260209", "name": "web_search"}


def _download_file(url: str, filename: str, data_dir: Path) -> str:
    data_dir.mkdir(parents=True, exist_ok=True)
    dest = data_dir / filename
    try:
        with httpx.stream("GET", url, follow_redirects=True, timeout=60.0) as resp:
            resp.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in resp.iter_bytes():
                    f.write(chunk)
    except Exception as exc:  # noqa: BLE001 — surfaced to Claude as a tool error, not raised
        return f"ERROR downloading {url}: {exc}"
    return f"Saved to {dest} ({dest.stat().st_size} bytes)"


def locate_and_download_filings(client: anthropic.Anthropic, task_prompt: str, data_dir: Path) -> list[Path]:
    """Phase A: tool-use loop — Claude searches the web and downloads
    candidate filing PDFs. Returns the list of successfully downloaded
    file paths."""
    tools = [WEB_SEARCH_TOOL, DOWNLOAD_TOOL]
    messages = [{"role": "user", "content": task_prompt}]
    downloaded: list[Path] = []

    for _ in range(MAX_TOOL_ITERATIONS):
        response = client.messages.create(
            model=MODEL, max_tokens=MAX_TOKENS, tools=tools, messages=messages,
        )

        if response.stop_reason == "pause_turn":
            # Server-side tool loop (web_search) hit its internal iteration cap —
            # re-send to let it continue, per the documented pause_turn contract.
            messages = [{"role": "user", "content": task_prompt},
                        {"role": "assistant", "content": response.content}]
            continue
        if response.stop_reason == "refusal":
            raise RuntimeError(f"Model declined the research request: {response.stop_details}")

        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
        if not tool_use_blocks:
            break  # end_turn with no pending tool calls — Claude is done searching

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in tool_use_blocks:
            if block.name != "download_file":
                continue
            result = _download_file(data_dir=data_dir, **block.input)
            if result.startswith("Saved to"):
                downloaded.append(data_dir / block.input["filename"])
            tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})
        if tool_results:
            messages.append({"role": "user", "content": tool_results})

    return downloaded


def _document_block(pdf_path: Path) -> dict:
    """Native PDF document content block — Claude reads it directly, no local
    text extraction needed for a well-formed PDF."""
    data = base64.standard_b64encode(pdf_path.read_bytes()).decode("utf-8")
    return {
        "type": "document",
        "source": {"type": "base64", "media_type": "application/pdf", "data": data},
        "title": pdf_path.name,
    }


def _repair_and_extract_text(pdf_path: Path) -> str:
    """Fallback for PDFs the API can't parse directly (malformed/truncated on
    disk, or over the size/page limit) — reuses the exact recovery toolchain
    this repo already proved out for Family Bank Kenya's broken source PDFs."""
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            if text.strip():
                return text
    except Exception:  # noqa: BLE001
        pass
    try:
        import pikepdf
        import pymupdf
        repaired = pdf_path.with_suffix(".repaired.pdf")
        pikepdf.open(pdf_path).save(repaired)
        doc = pymupdf.open(repaired)
        return "\n".join(page.get_text() for page in doc)
    except Exception as exc:  # noqa: BLE001
        return f"[COULD NOT EXTRACT TEXT FROM {pdf_path.name}: {exc}]"


def extract_facts(client: anthropic.Anthropic, pdf_paths: list[Path], extraction_prompt: str) -> str:
    """Phase B: feed the downloaded filings to Claude in one turn and ask for
    the two artifacts this repo's convention needs — a config.py body and a
    research_output.md body — as fenced code blocks in the response text."""
    content: list[dict] = []
    for pdf_path in pdf_paths:
        try:
            content.append(_document_block(pdf_path))
        except Exception:  # noqa: BLE001
            content.append({
                "type": "text",
                "text": f"[{pdf_path.name} contents, extracted locally after the native PDF path failed]\n"
                        + _repair_and_extract_text(pdf_path),
            })
    content.append({"type": "text", "text": extraction_prompt})

    response = client.messages.create(
        model=MODEL, max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": content}],
    )
    if response.stop_reason == "refusal":
        raise RuntimeError(f"Model declined the extraction request: {response.stop_details}")
    return "".join(b.text for b in response.content if b.type == "text")


def parse_artifacts(response_text: str) -> tuple[str, str]:
    """Pull the config.py and research_output.md bodies out of the model's
    fenced code blocks."""
    config_match = re.search(r"```python\s*\n(.*?)```", response_text, re.DOTALL)
    research_match = re.search(r"```markdown\s*\n(.*?)```", response_text, re.DOTALL)
    if not config_match or not research_match:
        raise ValueError(
            "Expected a ```python config.py block and a ```markdown research_output.md "
            "block in the model's response — got neither or only one. Full response:\n\n"
            + response_text
        )
    return config_match.group(1), research_match.group(1)
