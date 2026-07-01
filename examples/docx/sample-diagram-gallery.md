---
title: "Kroki Diagram Gallery Render Test"
department: "Platform Engineering"
status: "Draft"
version: "0.2"
date: "2026-07-01"
author: "Alex Gambino"
owner: "Platform Architecture"
audience:
  - Platform Engineering
  - Architecture Review Board
revision_history:
  - version: "0.2"
    date: "2026-07-01"
    author: "Alex Gambino"
    description: "Expanded sample to cover multiple Kroki-supported diagram languages"
---

## Overview

This document is a render test for the local Kroki-backed DOCX flow. Each
section shows a small source snippet followed by the rendered diagram so the
generated DOCX can be reviewed for layout, image scaling, and language support.

## Mermaid

Source:

```text
flowchart LR
    User --> Docs
    Docs --> Review
    Review --> Publish
```

Rendered:

```mermaid
flowchart LR
    User --> Docs
    Docs --> Review
    Review --> Publish
```

## PlantUML

Source:

```text
@startuml
actor User
participant Portal
database Repo
User -> Portal : request build
Portal -> Repo : fetch content
Repo --> Portal : content
Portal --> User : result
@enduml
```

Rendered:

```plantuml
@startuml
actor User
participant Portal
database Repo
User -> Portal : request build
Portal -> Repo : fetch content
Repo --> Portal : content
Portal --> User : result
@enduml
```

## Graphviz

Source:

```text
digraph G {
  rankdir=LR;
  Author -> Renderer;
  Renderer -> Assets;
  Assets -> Docx;
}
```

Rendered:

```graphviz
digraph G {
  rankdir=LR;
  Author -> Renderer;
  Renderer -> Assets;
  Assets -> Docx;
}
```

## D2

Source:

```text
devspace -> kroki: render
kroki -> assets: png
assets -> docx: embed
```

Rendered:

```d2
devspace -> kroki: render
kroki -> assets: png
assets -> docx: embed
```

## Structurizr

Source:

```text
workspace {
  model {
    user = person "Developer"
    docs = softwareSystem "Docs Flow"
    render = container docs "Renderer"
    kroki = container docs "Kroki"
    user -> render "renders"
    render -> kroki "requests diagram"
  }
  views {
    systemContext docs "context" {
      include *
      autolayout lr
    }
    theme default
  }
}
```

Rendered:

```structurizr
workspace {
  model {
    user = person "Developer"
    docs = softwareSystem "Docs Flow"
    render = container docs "Renderer"
    kroki = container docs "Kroki"
    user -> render "renders"
    render -> kroki "requests diagram"
  }
  views {
    systemContext docs "context" {
      include *
      autolayout lr
    }
    theme default
  }
}
```

## Pikchr

Source:

```text
box "Author" "writes markdown"
arrow
box "Renderer" "rewrites diagrams"
arrow
box "DOCX" "final output"
```

Rendered:

```pikchr
box "Author" "writes markdown"
arrow
box "Renderer" "rewrites diagrams"
arrow
box "DOCX" "final output"
```

## Review Notes

- Confirm each rendered diagram stays within a reasonable page footprint.
- Confirm the code snippets remain visible as text in the DOCX.
- Confirm the output works for Mermaid plus five additional diagram languages.
