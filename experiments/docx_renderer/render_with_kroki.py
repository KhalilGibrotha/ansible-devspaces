#!/usr/bin/env python3
"""Rewrite Kroki-supported fenced diagrams into PNG image references."""

from __future__ import annotations

import argparse
import os
import re
import urllib.request
from pathlib import Path
from typing import Callable

SUPPORTED_DIAGRAM_TYPES = {
    "mermaid": "mermaid",
    "plantuml": "plantuml",
    "c4plantuml": "c4plantuml",
    "graphviz": "graphviz",
    "dot": "graphviz",
    "d2": "d2",
    "pikchr": "pikchr",
    "erd": "erd",
    "svgbob": "svgbob",
    "nomnoml": "nomnoml",
    "structurizr": "structurizr",
    "ditaa": "ditaa",
    "seqdiag": "seqdiag",
    "blockdiag": "blockdiag",
    "nwdiag": "nwdiag",
    "packetdiag": "packetdiag",
    "rackdiag": "rackdiag",
    "umlet": "umlet",
    "vega": "vega",
    "vegalite": "vegalite",
    "wavedrom": "wavedrom",
    "wireviz": "wireviz",
    "dbml": "dbml",
    "bpmn": "bpmn",
    "excalidraw": "excalidraw",
    "bytefield": "bytefield",
    "goat": "goat",
}

FENCE_RE = re.compile(r"```([A-Za-z0-9_-]+)[^\n]*\n(.*?)\n```", re.DOTALL)


def render_diagram_png(diagram_type: str, diagram_source: str, kroki_url: str) -> bytes:
    """Render a Kroki-supported diagram to PNG bytes."""
    endpoint = f"{kroki_url.rstrip('/')}/{diagram_type}/png"
    request = urllib.request.Request(
        endpoint,
        data=diagram_source.encode("utf-8"),
        headers={"Content-Type": "text/plain; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def rewrite_markdown(
    markdown_text: str,
    *,
    output_markdown_path: Path,
    assets_dir: Path,
    renderer: Callable[[str], bytes],
) -> tuple[str, int]:
    """Replace supported diagram fences with image references and write PNG assets."""
    output_markdown_path.parent.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    rendered = 0
    rewritten_parts: list[str] = []
    last_index = 0

    for match in FENCE_RE.finditer(markdown_text):
        language = match.group(1).strip().lower()
        kroki_type = SUPPORTED_DIAGRAM_TYPES.get(language)
        if not kroki_type:
            continue
        rendered += 1
        rewritten_parts.append(markdown_text[last_index:match.start()])

        asset_name = f"{kroki_type}-{rendered:03d}.png"
        asset_path = assets_dir / asset_name
        asset_path.write_bytes(renderer(kroki_type, match.group(2).strip()))

        relative_asset_path = os.path.relpath(asset_path, output_markdown_path.parent)
        relative_asset_path = relative_asset_path.replace(os.sep, "/")
        human_label = language.upper() if language in {"d2", "dbml", "bpmn"} else language.capitalize()
        rewritten_parts.append(
            f"![Generated {human_label} diagram {rendered}]({relative_asset_path})"
        )
        last_index = match.end()

    rewritten_parts.append(markdown_text[last_index:])
    return "".join(rewritten_parts), rendered


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rewrite Kroki-supported fenced diagrams into PNG image references."
    )
    parser.add_argument("--input-markdown", required=True, type=Path)
    parser.add_argument("--output-markdown", required=True, type=Path)
    parser.add_argument("--assets-dir", required=True, type=Path)
    parser.add_argument("--kroki-url", default="http://kroki:8000")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_text = args.input_markdown.read_text(encoding="utf-8")
    rewritten_text, rendered = rewrite_markdown(
        source_text,
        output_markdown_path=args.output_markdown,
        assets_dir=args.assets_dir,
        renderer=lambda diagram_type, diagram: render_diagram_png(diagram_type, diagram, args.kroki_url),
    )
    args.output_markdown.write_text(rewritten_text, encoding="utf-8")
    print(
        f"Rendered {rendered} Kroki-supported diagram(s) from {args.input_markdown} "
        f"to {args.output_markdown} using {args.kroki_url}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
