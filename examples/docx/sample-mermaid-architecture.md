---
title: "Experimental DOCX Render Test"
department: "Platform Engineering"
status: "Draft"
version: "0.1"
date: "2026-07-01"
author: "Alex Gambino"
owner: "Platform Architecture"
audience:
  - Platform Engineering
  - Architecture Review Board
revision_history:
  - version: "0.1"
    date: "2026-07-01"
    author: "Alex Gambino"
    description: "Initial renderer test document"
---

## Overview

This document is a focused Mermaid smoke test for the experimental
Kroki-backed DOCX renderer.

## Architecture Flow

```mermaid
flowchart TD
    A[Author Markdown] --> B[Render Mermaid via Kroki]
    B --> C[Rewrite Markdown to PNG references]
    C --> D[Run docx-build]
    D --> E[Generate DOCX]
```

## Notes

- The renderer should replace the Mermaid fence with a PNG image reference.
- The DOCX output should keep heading numbering and body styling.
- The broader multi-language coverage test lives in
  `examples/docx/sample-diagram-gallery.md`.
