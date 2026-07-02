import tempfile
import unittest
from pathlib import Path

from scripts.lint_diagrams import first_line, iter_diagram_blocks, markdown_files


class DiagramLintTests(unittest.TestCase):
    def test_iter_diagram_blocks_finds_supported_fences_with_line_numbers(self):
        markdown = (
            "# Title\n\n"
            "```mermaid\nflowchart LR\nA-->B\n```\n\n"
            "```text\nnot a diagram\n```\n\n"
            "```plantuml\n@startuml\nA -> B\n@enduml\n```\n"
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "sample.md"
            file_path.write_text(markdown, encoding="utf-8")

            blocks = iter_diagram_blocks(file_path)

            self.assertEqual(2, len(blocks))
            self.assertEqual(("mermaid", "mermaid", 3), (blocks[0].language, blocks[0].kroki_type, blocks[0].line_number))
            self.assertEqual(("plantuml", "plantuml", 12), (blocks[1].language, blocks[1].kroki_type, blocks[1].line_number))

    def test_markdown_files_expands_directories(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "a.md").write_text("# A\n", encoding="utf-8")
            (root / "nested").mkdir()
            (root / "nested" / "b.md").write_text("# B\n", encoding="utf-8")
            (root / "ignore.txt").write_text("x", encoding="utf-8")

            files = markdown_files([str(root)])

            self.assertEqual([root / "a.md", root / "nested" / "b.md"], files)

    def test_first_line_handles_empty_source(self):
        self.assertEqual("<empty>", first_line("   "))


if __name__ == "__main__":
    unittest.main()
