# Documentation Workflow Integration Contract

This document captures the target contract between `ansible-devspaces` and
`dac-toolkit`.

## Contract

`ansible-devspaces` should treat `dac-toolkit` as the source of truth for
renderer behavior. The Dev Space layer supplies environment wiring and
convenience commands, but it should not redefine what a valid document render
means.

## Responsibilities by Layer

### Toolkit layer

- document parsing and DOCX generation
- diagram embedding behavior
- cover-page and logo behavior
- author-facing validation guidance
- stable schema decisions once ready

### Dev Space layer

- clone and bootstrap behavior
- workspace-local output roots
- local helper commands and make targets
- repo-discovery and manifest-discovery convenience
- platform-level smoke validation

## Inputs the Dev Space Layer Should Supply

- source repository checkout
- chosen manifest or manifest root
- optional workspace-local output root
- optional shared `org` and `logo` defaults
- local Kroki endpoint or equivalent render dependency

## Outputs the Dev Space Layer Should Expect

- deterministic rendered DOCX paths
- deterministic rewritten-markdown and generated-asset paths
- preflight, lint, and render failures that identify the failing layer

## Open Questions

1. Which manifest behaviors remain wrapper-only convenience and which should
   eventually move into the toolkit?
2. What is the preferred root-level convention for docs/content repos?
3. How persistent can the working output area be in the target Dev Spaces
   environment?
4. When should the docs-focused Dev Space split from the automation-focused Dev
   Space?
