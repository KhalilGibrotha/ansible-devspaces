import tempfile
import unittest
from pathlib import Path

from experiments.docx_renderer.render_with_kroki import rewrite_markdown


class RewriteMarkdownTests(unittest.TestCase):
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
