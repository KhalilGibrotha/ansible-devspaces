#!/usr/bin/env python3
"""Smoke-test a local Kroki sidecar by checking health and rendering Mermaid."""

from __future__ import annotations

import os
import sys
import urllib.error
import urllib.request


def fetch(url: str, *, data: bytes | None = None, content_type: str | None = None) -> bytes:
    headers = {}
    if content_type:
        headers["Content-Type"] = content_type
    request = urllib.request.Request(url, data=data, headers=headers, method="POST" if data is not None else "GET")
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read()


def main() -> int:
    kroki_url = os.environ.get("KROKI_URL", "http://127.0.0.1:8000").rstrip("/")
    try:
        health = fetch(f"{kroki_url}/health").decode("utf-8", errors="replace")
        if "ok" not in health.lower():
            print(f"Kroki health check returned unexpected response: {health}", file=sys.stderr)
            return 1

        diagram = b"flowchart TD\nA[Dev Space] --> B[Kroki Sidecar]\nB --> C[Rendered Diagram]\n"
        svg = fetch(f"{kroki_url}/mermaid/svg", data=diagram, content_type="text/plain; charset=utf-8")
        if b"<svg" not in svg:
            print("Kroki render response did not contain SVG output.", file=sys.stderr)
            return 1
    except urllib.error.URLError as exc:
        print(f"Failed to reach Kroki at {kroki_url}: {exc}", file=sys.stderr)
        return 1

    print(f"Kroki sidecar OK at {kroki_url}")
    print(f"Health: {health.strip()}")
    print(f"Rendered SVG bytes: {len(svg)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
