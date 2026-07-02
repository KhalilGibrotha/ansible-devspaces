#!/usr/bin/env python3
"""Manifest-driven DOCX lint/render wrapper."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = REPO_ROOT / "examples" / "docx" / "render-manifest.example.yaml"


@dataclass(frozen=True)
class DocumentSpec:
    id: str
    input: Path
    output: Path
    rewritten_markdown: Path
    assets_dir: Path
    org: Path | None
    logo: Path | None


def _resolve_path(raw_value: str | None) -> Path | None:
    if raw_value in (None, ""):
        return None
    path = Path(raw_value)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def load_manifest(path: Path) -> list[DocumentSpec]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    documents = data.get("documents")
    if not isinstance(documents, list) or not documents:
        raise ValueError(f"Manifest {path} does not define a non-empty 'documents' list.")

    specs: list[DocumentSpec] = []
    for index, entry in enumerate(documents, start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"Manifest entry {index} in {path} is not a mapping.")

        required = ("id", "input", "output", "rewritten_markdown", "assets_dir")
        missing = [key for key in required if not entry.get(key)]
        if missing:
            raise ValueError(f"Manifest entry {index} in {path} is missing: {', '.join(missing)}")

        specs.append(
            DocumentSpec(
                id=str(entry["id"]),
                input=_resolve_path(str(entry["input"])),
                output=_resolve_path(str(entry["output"])),
                rewritten_markdown=_resolve_path(str(entry["rewritten_markdown"])),
                assets_dir=_resolve_path(str(entry["assets_dir"])),
                org=_resolve_path(entry.get("org")),
                logo=_resolve_path(entry.get("logo")),
            )
        )

    return specs


def select_documents(specs: list[DocumentSpec], *, document_id: str | None) -> list[DocumentSpec]:
    if document_id is None:
        return specs
    if document_id == "":
        raise ValueError("A non-empty --document-id is required for single-document selection.")
    selected = [spec for spec in specs if spec.id == document_id]
    if not selected:
        available = ", ".join(spec.id for spec in specs)
        raise ValueError(f"Document id '{document_id}' not found. Available ids: {available}")
    return selected


def run_lint(spec: DocumentSpec, *, kroki_url: str, output_format: str) -> None:
    preflight_cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "preflight_docx.py"),
        str(spec.input),
    ]
    subprocess.run(preflight_cmd, check=True)

    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "lint_diagrams.py"),
        "--kroki-url",
        kroki_url,
        "--format",
        output_format,
        str(spec.input),
    ]
    subprocess.run(cmd, check=True)


def run_render(spec: DocumentSpec, *, kroki_url: str, toolkit_dir: Path | None, venv_dir: Path | None) -> None:
    env = os.environ.copy()
    env["INPUT_MARKDOWN"] = str(spec.input)
    env["OUTPUT_DOCX"] = str(spec.output)
    env["REWRITTEN_MARKDOWN"] = str(spec.rewritten_markdown)
    env["ASSETS_DIR"] = str(spec.assets_dir)
    env["KROKI_URL"] = kroki_url
    if spec.org:
        env["ORG_YAML"] = str(spec.org)
    if spec.logo:
        env["LOGO_PATH"] = str(spec.logo)
    if toolkit_dir:
        env["TOOLKIT_DIR"] = str(toolkit_dir)
    if venv_dir:
        env["VENV_DIR"] = str(venv_dir)

    subprocess.run(
        ["bash", str(REPO_ROOT / "scripts" / "docx-render-local.sh")],
        check=True,
        env=env,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manifest-driven DOCX lint/render wrapper.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common_args(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
        subparser.add_argument("--document-id", default=None)

    list_parser = subparsers.add_parser("list", help="List documents from the manifest.")
    add_common_args(list_parser)

    preflight_parser = subparsers.add_parser("preflight", help="Run static preflight checks for manifest-managed documents.")
    add_common_args(preflight_parser)

    lint_parser = subparsers.add_parser("lint", help="Lint manifest-managed documents.")
    add_common_args(lint_parser)
    lint_parser.add_argument("--kroki-url", default="http://127.0.0.1:8000")
    lint_parser.add_argument("--format", default="png", choices=("png", "svg"))

    render_parser = subparsers.add_parser("render", help="Render manifest-managed documents.")
    add_common_args(render_parser)
    render_parser.add_argument("--kroki-url", default="http://127.0.0.1:8000")
    render_parser.add_argument("--toolkit-dir", type=Path, default=None)
    render_parser.add_argument("--venv-dir", type=Path, default=None)

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = args.manifest if args.manifest.is_absolute() else REPO_ROOT / args.manifest
    specs = select_documents(load_manifest(manifest_path), document_id=getattr(args, "document_id", None))

    if args.command == "list":
        for spec in specs:
            print(f"{spec.id}: {spec.input} -> {spec.output}")
        return 0

    if args.command == "preflight":
        for spec in specs:
            print(f"[preflight] {spec.id}")
            subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "preflight_docx.py"),
                    str(spec.input),
                ],
                check=True,
            )
        return 0

    if args.command == "lint":
        for spec in specs:
            print(f"[lint] {spec.id}")
            run_lint(spec, kroki_url=args.kroki_url, output_format=args.format)
        return 0

    if args.command == "render":
        rendered_outputs: list[Path] = []
        for spec in specs:
            print(f"[render] {spec.id}")
            run_render(
                spec,
                kroki_url=args.kroki_url,
                toolkit_dir=args.toolkit_dir,
                venv_dir=args.venv_dir,
            )
            rendered_outputs.append(spec.output)
        print("\nRendered DOCX files:")
        for output in rendered_outputs:
            print(output)
        return 0

    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
