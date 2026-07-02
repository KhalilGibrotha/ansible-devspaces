import tempfile
import unittest
from pathlib import Path

from scripts.docx_manifest import apply_workspace_output_root, load_manifest, select_documents


class DocxManifestTests(unittest.TestCase):
    def test_load_manifest_parses_documents_with_defaults(self):
        manifest = """\
defaults:
  org: shared/org.yaml
  logo: shared/logo.png
documents:
  - id: architecture
    input: docs/publish/architecture.md
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
            self.assertTrue(str(specs[0].org).endswith("shared\\org.yaml") or str(specs[0].org).endswith("shared/org.yaml"))
            self.assertTrue(str(specs[0].logo).endswith("shared\\logo.png") or str(specs[0].logo).endswith("shared/logo.png"))

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

    def test_load_manifest_supports_child_manifests(self):
        root_manifest = """\
includes:
  - manifests/child.yaml
documents:
  - id: root-doc
    input: docs/root.md
"""
        child_manifest = """\
documents:
  - id: child-doc
    input: docs/child.md
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_root = Path(tmpdir)
            manifests_dir = manifest_root / "manifests"
            manifests_dir.mkdir()
            root_path = manifest_root / "render-manifest.yaml"
            child_path = manifests_dir / "child.yaml"
            root_path.write_text(root_manifest, encoding="utf-8")
            child_path.write_text(child_manifest, encoding="utf-8")

            specs = load_manifest(root_path)

            self.assertEqual(["child-doc", "root-doc"], [spec.id for spec in specs])
            self.assertTrue(str(specs[0].output).endswith("manifests\\build\\docx\\child.docx") or str(specs[0].output).endswith("manifests/build/docx/child.docx"))
            self.assertTrue(str(specs[1].output).endswith("build\\docx\\root.docx") or str(specs[1].output).endswith("build/docx/root.docx"))

    def test_load_manifest_rejects_duplicate_ids_across_child_manifests(self):
        root_manifest = """\
includes:
  - child-a.yaml
  - child-b.yaml
"""
        child_manifest = """\
documents:
  - id: duplicate-doc
    input: docs/example.md
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_root = Path(tmpdir)
            root_path = manifest_root / "render-manifest.yaml"
            child_a_path = manifest_root / "child-a.yaml"
            child_b_path = manifest_root / "child-b.yaml"
            root_path.write_text(root_manifest, encoding="utf-8")
            child_a_path.write_text(child_manifest, encoding="utf-8")
            child_b_path.write_text(child_manifest, encoding="utf-8")

            with self.assertRaises(ValueError):
                load_manifest(root_path)

    def test_load_manifest_rejects_include_cycles(self):
        root_manifest = """\
includes:
  - child.yaml
"""
        child_manifest = """\
includes:
  - render-manifest.yaml
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_root = Path(tmpdir)
            root_path = manifest_root / "render-manifest.yaml"
            child_path = manifest_root / "child.yaml"
            root_path.write_text(root_manifest, encoding="utf-8")
            child_path.write_text(child_manifest, encoding="utf-8")

            with self.assertRaises(ValueError):
                load_manifest(root_path)

    def test_load_manifest_inherits_defaults_into_child_manifests(self):
        root_manifest = """\
defaults:
  org: shared/org.yaml
  logo: shared/logo.png
  output_root: artifacts
includes:
  - manifests/child.yaml
"""
        child_manifest = """\
documents:
  - id: child-doc
    input: docs/child.md
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_root = Path(tmpdir)
            manifests_dir = manifest_root / "manifests"
            manifests_dir.mkdir()
            root_path = manifest_root / "render-manifest.yaml"
            child_path = manifests_dir / "child.yaml"
            root_path.write_text(root_manifest, encoding="utf-8")
            child_path.write_text(child_manifest, encoding="utf-8")

            specs = load_manifest(root_path)

            self.assertEqual(["child-doc"], [spec.id for spec in specs])
            self.assertTrue(str(specs[0].org).endswith("shared\\org.yaml") or str(specs[0].org).endswith("shared/org.yaml"))
            self.assertTrue(str(specs[0].logo).endswith("shared\\logo.png") or str(specs[0].logo).endswith("shared/logo.png"))
            self.assertTrue(str(specs[0].output).endswith("artifacts\\docx\\child.docx") or str(specs[0].output).endswith("artifacts/docx/child.docx"))

    def test_document_fields_override_manifest_defaults(self):
        manifest = """\
defaults:
  org: shared/org.yaml
  logo: shared/logo.png
  output_root: artifacts
documents:
  - id: architecture
    input: docs/publish/architecture.md
    org: overrides/custom-org.yaml
    logo: overrides/custom-logo.jpg
    output: exports/custom.docx
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.yaml"
            manifest_path.write_text(manifest, encoding="utf-8")

            specs = load_manifest(manifest_path)

            self.assertTrue(str(specs[0].org).endswith("overrides\\custom-org.yaml") or str(specs[0].org).endswith("overrides/custom-org.yaml"))
            self.assertTrue(str(specs[0].logo).endswith("overrides\\custom-logo.jpg") or str(specs[0].logo).endswith("overrides/custom-logo.jpg"))
            self.assertTrue(str(specs[0].output).endswith("exports\\custom.docx") or str(specs[0].output).endswith("exports/custom.docx"))

    def test_apply_workspace_output_root_relocates_repo_relative_outputs(self):
        manifest = """\
defaults:
  output_root: docs/build
documents:
  - id: architecture
    input: docs/publish/architecture.md
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir) / "architecture-docs"
            repo_root.mkdir()
            (repo_root / ".git").mkdir()
            manifest_path = repo_root / "render-manifest.yaml"
            manifest_path.write_text(manifest, encoding="utf-8")

            specs = load_manifest(manifest_path)
            relocated = apply_workspace_output_root(
                specs,
                manifest_path=manifest_path,
                workspace_output_root=repo_root.parent / ".docx-work",
            )

            self.assertTrue(str(relocated[0].output).endswith(".docx-work\\architecture-docs\\docs\\build\\docx\\architecture.docx") or str(relocated[0].output).endswith(".docx-work/architecture-docs/docs/build/docx/architecture.docx"))
            self.assertTrue(str(relocated[0].rewritten_markdown).endswith(".docx-work\\architecture-docs\\docs\\build\\rewritten\\architecture.md") or str(relocated[0].rewritten_markdown).endswith(".docx-work/architecture-docs/docs/build/rewritten/architecture.md"))
            self.assertTrue(str(relocated[0].assets_dir).endswith(".docx-work\\architecture-docs\\docs\\build\\diagrams\\architecture") or str(relocated[0].assets_dir).endswith(".docx-work/architecture-docs/docs/build/diagrams/architecture"))

    def test_apply_workspace_output_root_leaves_external_outputs_unchanged(self):
        manifest = """\
documents:
  - id: architecture
    input: docs/publish/architecture.md
    output: /tmp/custom.docx
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir) / "architecture-docs"
            repo_root.mkdir()
            (repo_root / ".git").mkdir()
            manifest_path = repo_root / "render-manifest.yaml"
            manifest_path.write_text(manifest, encoding="utf-8")

            specs = load_manifest(manifest_path)
            relocated = apply_workspace_output_root(
                specs,
                manifest_path=manifest_path,
                workspace_output_root=repo_root.parent / ".docx-work",
            )

            self.assertEqual(specs[0].output, relocated[0].output)


if __name__ == "__main__":
    unittest.main()
