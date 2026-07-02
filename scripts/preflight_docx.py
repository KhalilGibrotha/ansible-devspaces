#!/usr/bin/env python3
"""Static pre-render checks for DOCX-targeted Markdown."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.docx_renderer.render_with_kroki import FENCE_RE, SUPPORTED_DIAGRAM_TYPES

SUSPICIOUS_MOJIBAKE_TOKENS = (
    "�",
    "Â«",
    "Â»",
    "â€”",
    "â€“",
    "â€œ",
    "â€",
    "â€™",
    "â€¢",
)


@dataclass(frozen=True)
class PreflightFinding:
    severity: str
    file_path: Path
    line_number: int
    message: str


def line_number_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def load_text(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8")


def check_front_matter(file_path: Path, text: str) -> list[PreflightFinding]:
    findings: list[PreflightFinding] = []
    if not text.startswith("---\n"):
        findings.append(PreflightFinding("WARN", file_path, 1, "Missing YAML front matter block."))
        return findings

    end = text.find("\n---\n", 4)
    if end == -1:
        findings.append(PreflightFinding("ERROR", file_path, 1, "Unterminated YAML front matter block."))
        return findings

    front_matter = text[4:end]
    try:
        data = yaml.safe_load(front_matter) or {}
    except yaml.YAMLError as exc:
        findings.append(PreflightFinding("ERROR", file_path, 1, f"Invalid YAML front matter: {exc}"))
        return findings

    for key in ("title", "doc_type", "owner", "version", "date"):
        if not data.get(key):
            findings.append(PreflightFinding("WARN", file_path, 1, f"Front matter is missing recommended key '{key}'."))

    return findings


def check_mojibake(file_path: Path, text: str) -> list[PreflightFinding]:
    findings: list[PreflightFinding] = []
    for token in SUSPICIOUS_MOJIBAKE_TOKENS:
        start = 0
        while True:
            idx = text.find(token, start)
            if idx == -1:
                break
            findings.append(
                PreflightFinding(
                    "ERROR",
                    file_path,
                    line_number_for_offset(text, idx),
                    f"Suspicious mojibake token '{token}' detected; source encoding likely needs correction.",
                )
            )
            start = idx + len(token)
    return findings


def check_diagram_fences(file_path: Path, text: str) -> list[PreflightFinding]:
    findings: list[PreflightFinding] = []
    for match in FENCE_RE.finditer(text):
        language = match.group(1).strip().lower()
        line_number = line_number_for_offset(text, match.start())
        if language == "text":
            continue
        if language not in SUPPORTED_DIAGRAM_TYPES and language not in {"yaml", "bash", "text", "json"}:
            findings.append(
                PreflightFinding(
                    "WARN",
                    file_path,
                    line_number,
                    f"Fence language '{language}' is not currently rendered by the DOCX diagram pipeline.",
                )
            )
    return findings


def run_preflight(file_path: Path) -> list[PreflightFinding]:
    text = load_text(file_path)
    findings: list[PreflightFinding] = []
    findings.extend(check_front_matter(file_path, text))
    findings.extend(check_mojibake(file_path, text))
    findings.extend(check_diagram_fences(file_path, text))
    return findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run static pre-render checks for DOCX-targeted Markdown.")
    parser.add_argument("paths", nargs="+", help="Markdown files to check.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    findings: list[PreflightFinding] = []
    for raw_path in args.paths:
        file_path = Path(raw_path)
        findings.extend(run_preflight(file_path))

    if not findings:
        print("Preflight OK")
        return 0

    highest = 0
    severity_rank = {"WARN": 1, "ERROR": 2}
    for finding in findings:
        highest = max(highest, severity_rank[finding.severity])
        print(f"{finding.severity} {finding.file_path}:{finding.line_number}: {finding.message}")

    return 1 if highest >= 2 else 0


if __name__ == "__main__":
    raise SystemExit(main())
