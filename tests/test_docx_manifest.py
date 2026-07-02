import tempfile
import unittest
from pathlib import Path

from scripts.docx_manifest import load_manifest, select_documents


class DocxManifestTests(unittest.TestCase):
    def test_load_manifest_parses_documents_with_defaults(self):
        manifest = """\
documents:
  - id: architecture
    input: docs/publish/architecture.md
    org: examples/docx/org.yaml
    logo: ""
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.yaml"
            manifest_path.write_text(manifest, encoding="utf-8")

            specs = load_manifest(manifest_path)

            self.assertEqual(1, len(specs))
            self.assertEqual("architecture", specs[0].id)
            self.assertTrue(str(specs[0].input).endswith("docs\\publish\\architecture.md") or str(specs[0].input).endswith("docs/publish/architecture.md"))
            self.assertTrue(str(specs[0].output).endswith("build\\docx\\architecture.docx") or str(specs[0].output).endswith("build/docx/architecture.docx"))
            self.assertTrue(str(specs[0].rewritten_markdown).endswith("build\\rewritten\\architecture.md") or str(specs[0].rewritten_markdown).endswith("build/rewritten/architecture.md"))
            self.assertTrue(str(specs[0].assets_dir).endswith("build\\diagrams\\architecture") or str(specs[0].assets_dir).endswith("build/diagrams/architecture"))

    def test_select_documents_filters_by_id(self):
        manifest = """\
documents:
  - id: architecture
    input: docs/publish/architecture.md
    output: docs/build/docx/architecture.docx
    rewritten_markdown: docs/build/rewritten/architecture.md
    assets_dir: docs/build/diagrams/architecture
  - id: runbook
    input: docs/publish/runbook.md
    output: docs/build/docx/runbook.docx
    rewritten_markdown: docs/build/rewritten/runbook.md
    assets_dir: docs/build/diagrams/runbook
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.yaml"
            manifest_path.write_text(manifest, encoding="utf-8")

            specs = load_manifest(manifest_path)
            selected = select_documents(specs, document_id="runbook")

            self.assertEqual(["runbook"], [spec.id for spec in selected])

    def test_select_documents_rejects_empty_single_document_id(self):
        manifest = """\
documents:
  - id: architecture
    input: docs/publish/architecture.md
    output: docs/build/docx/architecture.docx
    rewritten_markdown: docs/build/rewritten/architecture.md
    assets_dir: docs/build/diagrams/architecture
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.yaml"
            manifest_path.write_text(manifest, encoding="utf-8")

            specs = load_manifest(manifest_path)
            with self.assertRaises(ValueError):
                select_documents(specs, document_id="")

    def test_load_manifest_supports_output_name_override(self):
        manifest = """\
documents:
  - id: playbook-readme
    input: playbooks/example/README.md
    output_name: Example Playbook Guide
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "render-manifest.yaml"
            manifest_path.write_text(manifest, encoding="utf-8")

            specs = load_manifest(manifest_path)

            self.assertEqual("playbook-readme", specs[0].id)
            self.assertTrue(str(specs[0].output).endswith("build\\docx\\Example Playbook Guide.docx") or str(specs[0].output).endswith("build/docx/Example Playbook Guide.docx"))
            self.assertTrue(str(specs[0].rewritten_markdown).endswith("build\\rewritten\\Example Playbook Guide.md") or str(specs[0].rewritten_markdown).endswith("build/rewritten/Example Playbook Guide.md"))
            self.assertTrue(str(specs[0].assets_dir).endswith("build\\diagrams\\Example Playbook Guide") or str(specs[0].assets_dir).endswith("build/diagrams/Example Playbook Guide"))


if __name__ == "__main__":
    unittest.main()
