#!/usr/bin/env python3
"""Rewrite Mermaid fences into PNG image references using a Kroki endpoint."""

from __future__ import annotations

import argparse
import os
import re
import urllib.request
from pathlib import Path
from typing import Callable

MERMAID_FENCE_RE = re.compile(r"```mermaid[^\n]*\n(.*?)\n```", re.DOTALL)


def render_mermaid_png(diagram_source: str, kroki_url: str) -> bytes:
    """Render a Mermaid diagram to PNG bytes using Kroki."""
    endpoint = f"{kroki_url.rstrip('/')}/mermaid/png"
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
    """Replace Mermaid fences with image references and write PNG assets."""
    output_markdown_path.parent.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    rendered = 0
    rewritten_parts: list[str] = []
    last_index = 0

    for match in MERMAID_FENCE_RE.finditer(markdown_text):
        rendered += 1
        rewritten_parts.append(markdown_text[last_index:match.start()])

        asset_name = f"mermaid-{rendered:03d}.png"
        asset_path = assets_dir / asset_name
        asset_path.write_bytes(renderer(match.group(1).strip()))

        relative_asset_path = os.path.relpath(asset_path, output_markdown_path.parent)
        relative_asset_path = relative_asset_path.replace(os.sep, "/")
        rewritten_parts.append(
            f"![Generated Mermaid diagram {rendered}]({relative_asset_path})"
        )
        last_index = match.end()

    rewritten_parts.append(markdown_text[last_index:])
    return "".join(rewritten_parts), rendered


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rewrite Mermaid fences into Kroki-rendered PNG image references."
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
        renderer=lambda diagram: render_mermaid_png(diagram, args.kroki_url),
    )
    args.output_markdown.write_text(rewritten_text, encoding="utf-8")
    print(
        f"Rendered {rendered} Mermaid diagram(s) from {args.input_markdown} "
        f"to {args.output_markdown} using {args.kroki_url}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
