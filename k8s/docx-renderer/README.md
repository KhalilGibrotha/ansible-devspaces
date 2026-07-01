# Experimental DOCX Renderer

This directory contains an isolated rendering path for Markdown-to-DOCX builds
that need Mermaid support without baking extra packages into the base Dev Space.

The flow is:

1. Deploy a Kroki service inside the namespace.
2. Run a short-lived Python job pod that:
   - rewrites Mermaid fences to PNG assets with Kroki
   - installs `docx-builder` from the cloned `dac-toolkit` repo
   - invokes `docx-build` against the rewritten Markdown

Use the helper script from the repository root:

```bash
bash ./scripts/docx-renderer.sh apply-kroki
WORKSPACE_PVC=my-workspace-pvc \
INPUT_MARKDOWN=/workspace/content/docs/sample.md \
OUTPUT_DOCX=/workspace/content/exports/sample.docx \
bash ./scripts/docx-renderer.sh run-job
bash ./scripts/docx-renderer.sh wait-job
bash ./scripts/docx-renderer.sh logs-job
```

The job manifest assumes the workspace PVC already contains both
`ansible-devspaces` and `dac-toolkit`.
