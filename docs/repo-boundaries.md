# Dev Space Integration Boundaries

This document defines what `ansible-devspaces` should own as the documentation
workflow is split away from the core renderer.

## Purpose

This repository should remain an automation-focused Dev Space that can also
consume documentation tooling. It should not become the long-term home of core
DOCX rendering behavior.

## This Repo Should Own

- Dev Space bootstrap and startup behavior
- Automation-focused repo cloning and workspace assembly
- Local convenience commands that call the documentation workflow
- Platform-specific environment setup such as working directories, mounted
  storage, and path conventions
- Integration tests that verify the docs workflow behaves correctly inside this
  Dev Space

## This Repo Should Avoid Owning

- Core DOCX layout logic
- Renderer-specific image or pagination policy
- Duplicate definitions of authoring conventions already documented in
  `dac-toolkit`
- A second long-lived implementation of manifest semantics once those semantics
  stabilize

## Near-Term Responsibilities

1. Provide a clean `docx-render-one` entrypoint by manifest `id`.
2. Provide manifest discovery and child-manifest experiments.
3. Provision an unversioned working area for rendered outputs.
4. Standardize bootstrap so repos clone reliably in the workspace.
5. Exercise the workflow against real content repositories and classify
   failures at the correct layer.

## Target End State

If documentation workflow becomes a first-class, ongoing use case, the likely
end state is:

- `dac-toolkit` becomes the source of truth for docs workflow behavior.
- a dedicated docs-focused Dev Space consumes `dac-toolkit` directly.
- `ansible-devspaces` keeps only the minimum bridge needed for automation teams
  that occasionally need documentation rendering.
