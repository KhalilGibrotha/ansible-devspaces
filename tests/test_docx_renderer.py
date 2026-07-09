import tempfile
import unittest
from pathlib import Path
from unittest import mock

from experiments.docx_renderer.render_with_kroki import (
    DiagramRenderError,
    build_render_endpoint,
    ensure_png_bytes,
    get_render_scale,
    rewrite_markdown,
)


class RewriteMarkdownTests(unittest.TestCase):
    def test_get_render_scale_prefers_generic_env(self):
        with mock.patch.dict(
            "os.environ",
            {
                "DOCX_BUILDER_DIAGRAM_RENDER_SCALE": "3",
                "KROKI_RENDER_SCALE": "2",
            },
            clear=False,
        ):
            self.assertEqual(get_render_scale(), 3.0)

    def test_get_render_scale_clamps_and_falls_back(self):
        with mock.patch.dict(
            "os.environ",
            {"DOCX_BUILDER_DIAGRAM_RENDER_SCALE": "bad"},
            clear=False,
        ):
            self.assertEqual(get_render_scale(), 2.0)

        with mock.patch.dict(
            "os.environ",
            {"DOCX_BUILDER_DIAGRAM_RENDER_SCALE": "0.5"},
            clear=False,
        ):
            self.assertEqual(get_render_scale(), 1.0)

        with mock.patch.dict(
            "os.environ",
            {"DOCX_BUILDER_DIAGRAM_RENDER_SCALE": "5"},
            clear=False,
        ):
            self.assertEqual(get_render_scale(), 4.0)

    def test_build_render_endpoint_includes_scale(self):
        endpoint = build_render_endpoint(
            "http://127.0.0.1:8000",
            "packetdiag",
            "png",
            scale=2.5,
        )
        self.assertEqual(
            endpoint,
            "http://127.0.0.1:8000/packetdiag/png?scale=2.5",
        )

    def test_ensure_png_bytes_rejects_non_png_payload(self):
        with self.assertRaises(DiagramRenderError) as ctx:
            ensure_png_bytes(
                b"<svg>not png</svg>",
                diagram_type="packetdiag",
                endpoint="http://127.0.0.1:8000/packetdiag/png",
            )

        self.assertIn("non-PNG payload", str(ctx.exception))

    def test_leaves_markdown_without_mermaid_unchanged(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_markdown = root / "rewritten.md"
            assets_dir = root / "assets"

            rewritten, rendered = rewrite_markdown(
                "# Title\n\nNo diagrams here.\n",
                output_markdown_path=output_markdown,
                assets_dir=assets_dir,
                renderer=lambda _: b"png-bytes",
            )

            self.assertEqual(rendered, 0)
            self.assertEqual(rewritten, "# Title\n\nNo diagrams here.\n")
            self.assertEqual(list(assets_dir.iterdir()), [])

    def test_rewrites_mermaid_fences_to_relative_png_links(self):
        markdown = (
            "# Title\n\n"
            "```mermaid\n"
            "graph TD\n"
            "  A-->B\n"
            "```\n\n"
            "After diagram.\n"
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_markdown = root / "nested" / "rewritten.md"
            assets_dir = root / "nested" / "assets"

            rewritten, rendered = rewrite_markdown(
                markdown,
                output_markdown_path=output_markdown,
                assets_dir=assets_dir,
                renderer=lambda diagram_type, diagram: f"{diagram_type}:{diagram}".encode("utf-8"),
            )

            self.assertEqual(rendered, 1)
            self.assertIn(
                "![Generated Mermaid diagram 1](assets/mermaid-001.png)",
                rewritten,
            )
            self.assertEqual(
                (assets_dir / "mermaid-001.png").read_bytes(),
                b"mermaid:graph TD\n  A-->B",
            )

    def test_numbers_multiple_diagrams_deterministically(self):
        markdown = (
            "```mermaid\nflowchart LR\nA-->B\n```\n\n"
            "```mermaid\nflowchart LR\nB-->C\n```\n"
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_markdown = root / "rewritten.md"
            assets_dir = root / "generated"

            rewritten, rendered = rewrite_markdown(
                markdown,
                output_markdown_path=output_markdown,
                assets_dir=assets_dir,
                renderer=lambda diagram_type, diagram: diagram.encode("utf-8"),
            )

            self.assertEqual(rendered, 2)
            self.assertIn("generated/mermaid-001.png", rewritten)
            self.assertIn("generated/mermaid-002.png", rewritten)

    def test_rewrites_supported_non_mermaid_diagram_fences(self):
        markdown = (
            "```plantuml\n@startuml\nAlice -> Bob: hi\n@enduml\n```\n"
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_markdown = root / "rewritten.md"
            assets_dir = root / "generated"

            rewritten, rendered = rewrite_markdown(
                markdown,
                output_markdown_path=output_markdown,
                assets_dir=assets_dir,
                renderer=lambda diagram_type, diagram: f"{diagram_type}:{diagram}".encode("utf-8"),
            )

            self.assertEqual(rendered, 1)
            self.assertIn("![Generated Plantuml diagram 1](generated/plantuml-001.png)", rewritten)
            self.assertEqual(
                (assets_dir / "plantuml-001.png").read_bytes(),
                b"plantuml:@startuml\nAlice -> Bob: hi\n@enduml",
            )


if __name__ == "__main__":
    unittest.main()
