#!/usr/bin/env python3
"""Validate Kroki-supported fenced diagrams before rendering DOCX output."""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.docx_renderer.render_with_kroki import FENCE_RE, SUPPORTED_DIAGRAM_TYPES


@dataclass(frozen=True)
class DiagramBlock:
    file_path: Path
    language: str
    kroki_type: str
    line_number: int
    source: str


def iter_diagram_blocks(file_path: Path) -> list[DiagramBlock]:
    text = file_path.read_text(encoding="utf-8")
    blocks: list[DiagramBlock] = []
    for match in FENCE_RE.finditer(text):
        language = match.group(1).strip().lower()
        kroki_type = SUPPORTED_DIAGRAM_TYPES.get(language)
        if not kroki_type:
            continue
        line_number = text.count("\n", 0, match.start()) + 1
        blocks.append(
            DiagramBlock(
                file_path=file_path,
                language=language,
                kroki_type=kroki_type,
                line_number=line_number,
                source=match.group(2).strip(),
            )
        )
    return blocks


def validate_diagram(block: DiagramBlock, kroki_url: str) -> None:
    endpoint = f"{kroki_url.rstrip('/')}/{block.kroki_type}/svg"
    request = urllib.request.Request(
        endpoint,
        data=block.source.encode("utf-8"),
        headers={"Content-Type": "text/plain; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60):
            return
    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            f"{block.file_path}:{block.line_number}: "
            f"{block.language} rejected by Kroki at {endpoint}: HTTP {exc.code} {exc.reason}. "
            f"First line: {first_line(block.source)}"
        ) from exc


def first_line(source: str) -> str:
    stripped = source.strip().splitlines()
    return stripped[0] if stripped else "<empty>"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Kroki-supported fenced diagram blocks in Markdown files."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["examples/docx"],
        help="Markdown files or directories to scan. Defaults to examples/docx.",
    )
    parser.add_argument("--kroki-url", default="http://127.0.0.1:8000")
    return parser.parse_args()


def markdown_files(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_dir():
            files.extend(sorted(path.rglob("*.md")))
        elif path.is_file():
            files.append(path)
        else:
            raise FileNotFoundError(f"Path not found: {path}")
    return files


def main() -> int:
    args = parse_args()
    files = markdown_files(args.paths)
    blocks: list[DiagramBlock] = []
    for file_path in files:
        blocks.extend(iter_diagram_blocks(file_path))

    if not blocks:
        print("No Kroki-supported diagram blocks found.")
        return 0

    failures: list[str] = []
    for block in blocks:
        try:
            validate_diagram(block, args.kroki_url)
            print(f"OK  {block.file_path}:{block.line_number} [{block.language}]")
        except RuntimeError as exc:
            failures.append(str(exc))
            print(f"FAIL {exc}", file=sys.stderr)

    if failures:
        print(f"\n{len(failures)} diagram validation failure(s).", file=sys.stderr)
        return 1

    print(f"\nValidated {len(blocks)} diagram block(s) via Kroki.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
