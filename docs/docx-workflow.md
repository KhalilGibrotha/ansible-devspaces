# DOCX Workflow

This document describes the current DOCX rendering workflow in this repository
and the recommended next-step design for scaling it to multiple source
documents.

## Current State

The repository currently supports a single-document, local-first DOCX render
workflow driven by explicit paths and environment variables, plus a first-pass
manifest runner for batch lint/render operations.

Current capabilities:

- `make kroki-sidecar-test` verifies the local Kroki sidecar.
- `make diagram-lint` scans Markdown for Kroki-supported fenced diagrams and
  validates them against the local Kroki `/png` endpoints.
- `make diagram-lint-all` reads the default manifest and validates every
  manifest-managed document.
- `make docx-render-local`:
  - ensures `dac-toolkit` is cloned into `workspace-repos/`
  - installs `docx_builder` into a local virtual environment
  - validates diagram fences in the selected input Markdown
  - rewrites diagram fences into generated PNG assets
  - runs `docx-build` to produce a DOCX
- `make docx-render-all` reads the default manifest and renders every
  manifest-managed document through the existing local DOCX path.
- `make docx-render-one DOC_ID=...` renders a single manifest-managed document.

Current limitations:

- The batch runner executes the existing one-document render script per
  manifest entry, so environment setup is reused but not yet optimized as a
  single in-process build graph.
- Manifest paths are repo-root-relative and intentionally simple for now.
- Diagram source reuse across documents is a convention, not a first-class
  feature.
- Generated diagram assets are tied to a single document render run rather than
  being organized as reusable build outputs for a docs set.

Current quality control:

- `DOCX_BUILDER_DIAGRAM_RENDER_SCALE` defaults to `2` for local and job-based
  Kroki renders.
- The same scale applies to every Kroki-backed diagram type validated by
  `make diagram-lint` and rewritten during DOCX rendering.
- Raise it to `3` for especially dense diagrams when sharper PNG output is
  more important than render time or asset size.

## Recommended Direction

For documentation-heavy repositories, move from ad hoc single-file rendering to
an explicit manifest-driven build.

The core design principles are:

- Explicit inclusion:
  only documents listed in a manifest are rendered to DOCX.
- Separate lint and build stages:
  validate diagram source early, then build DOCX outputs intentionally.
- Stable build locations:
  place generated artifacts and rendered diagram images under a dedicated build
  directory rather than scattering them beside source documents.
- Reusable diagram sources:
  keep shared diagram code in dedicated source files when the same diagram or
  diagram fragment is referenced by multiple documents.

## Proposed Repository Layout

One workable layout looks like this:

```text
docs/
  publish/
    architecture.md
    runbook.md
    onboarding.md
  shared/
    diagrams/
      system-context.puml
      deployment-flow.mmd
      support-handoff.dot
    snippets/
      architecture-decision.md
      service-boundary.md
  build/
    docx/
    rewritten/
    diagrams/
  render-manifest.yaml
```

Recommended meaning:

- `docs/publish/`:
  authoritative Markdown documents intended for DOCX output.
- `docs/shared/diagrams/`:
  reusable diagram source files stored once and referenced intentionally.
- `docs/shared/snippets/`:
  reusable prose/code fragments for authorship discipline.
- `docs/build/docx/`:
  generated DOCX outputs.
- `docs/build/rewritten/`:
  intermediate Markdown after diagram fence rewriting.
- `docs/build/diagrams/`:
  generated PNG assets emitted during render.

## Manifest Model

Use a manifest to define the documents that are renderable and their output
settings.

Example:

```yaml
documents:
  - id: architecture
    input: docs/publish/architecture.md
    output: docs/build/docx/architecture.docx
    rewritten_markdown: docs/build/rewritten/architecture.md
    assets_dir: docs/build/diagrams/architecture
    org: examples/docx/org.yaml
    logo: ""

  - id: onboarding
    input: docs/publish/onboarding.md
    output: docs/build/docx/onboarding.docx
    rewritten_markdown: docs/build/rewritten/onboarding.md
    assets_dir: docs/build/diagrams/onboarding
    org: examples/docx/org.yaml
    logo: ""
```

Why a manifest is preferable:

- supports multiple outputs cleanly
- avoids accidental rendering of random Markdown files
- allows per-document branding and output paths
- creates a stable contract for CI

## DRY Diagram Reuse

For shared diagrams, the best approach is to treat diagram source like any
other reusable source artifact.

Recommended practice:

- Store shared diagram code in `docs/shared/diagrams/`
- Give each file a source-native extension when helpful:
  - `.puml`
  - `.mmd`
  - `.dot`
  - `.diag`
- Reference or include them into publishable documents intentionally rather
  than duplicating large diagram blocks everywhere

Two good reuse models:

1. Source-of-truth file plus document-local render block

   Authors keep the canonical diagram in a shared file and copy small stable
   fences into specific docs only when the doc truly needs an embedded render.

2. Source-of-truth file plus pre-build inclusion

   A future manifest-aware preprocessor could inject shared diagram content
   into a document before Kroki validation and DOCX rendering.

For current-state simplicity, model `1` is safer. It keeps the workflow
transparent and avoids building an inclusion engine too early.

## Recommended Command Surface

The repository now has a minimal first-pass manifest command surface:

```text
make diagram-lint
make diagram-lint-all
make docx-render-one DOC_ID=architecture
make docx-render-all
```

Suggested meanings:

- `make diagram-lint`:
  lint the default manifest set or a user-provided subset.
- `make diagram-lint-all`:
  lint every manifest entry.
- `make docx-render-one`:
  render a single document intentionally.
- `make docx-render-all`:
  render every manifest entry into the build directory.

The current implementation uses:

```text
MANIFEST ?= docs/render-manifest.yaml
make docx-render-one DOC_ID=sample-gallery
```

The sample reference manifest remains at
`examples/docx/render-manifest.example.yaml` for comparison and experimentation.

## CI / DaC Flow

For a docs-focused repository, the recommended DaC flow is:

1. Authors work in `docs/publish/`
2. Authors preview Markdown and diagrams in the IDE
3. `make diagram-lint` runs locally and in CI
4. `make docx-render-all` runs on demand or in a release-oriented pipeline
5. DOCX artifacts are published from `docs/build/docx/`

Recommended CI policy:

- Pull requests:
  run diagram lint only for manifest-managed docs
- Main branch or release branch:
  render DOCX artifacts for manifest-managed docs

## Current Recommendation

Do not auto-render every Markdown file that happens to contain a diagram fence.

Prefer this policy instead:

- only documents listed in the manifest are publishable
- only manifest-managed documents participate in DOCX lint/build flows
- literal code examples remain ordinary Markdown unless intentionally rendered

That keeps the system predictable for both documentation repositories and
mixed code-and-docs repositories.
