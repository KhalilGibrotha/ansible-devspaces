import tempfile
import unittest
from pathlib import Path

from scripts.preflight_docx import run_preflight


class PreflightDocxTests(unittest.TestCase):
    def test_detects_mojibake_tokens(self):
        markdown = """\
---
title: "Example"
doc_type: "sad"
owner: "Architecture"
version: "0.1"
date: "2026-07-02"
---

This line contains â€” mojibake.
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "sample.md"
            file_path.write_text(markdown, encoding="utf-8")

            findings = run_preflight(file_path)

            self.assertTrue(any("mojibake" in finding.message for finding in findings))

    def test_warns_when_front_matter_missing(self):
        markdown = "# Title\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "sample.md"
            file_path.write_text(markdown, encoding="utf-8")

            findings = run_preflight(file_path)

            self.assertTrue(any("Missing YAML front matter" in finding.message for finding in findings))


if __name__ == "__main__":
    unittest.main()
