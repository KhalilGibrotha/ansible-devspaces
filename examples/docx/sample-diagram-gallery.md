---
title: "Kroki Diagram Gallery Render Test"
department: "Platform Engineering"
status: "Draft"
version: "0.6"
date: "2026-07-01"
author: "Alex Gambino"
owner: "Platform Architecture"
audience:
  - Platform Engineering
  - Architecture Review Board
revision_history:
  - version: "0.6"
    date: "2026-07-01"
    author: "Alex Gambino"
    description: "Expanded sample to cover multiple Kroki-supported diagram languages with stable PNG-friendly examples"
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

## Packetdiag

Source:

```text
packetdiag {
  colwidth = 28;
  node_height = 72;
  internet [label = "Client"];
  gateway [label = "Kroki"];
  docx [label = "DOCX"];
  internet -> gateway -> docx;
}
```

Rendered:

```packetdiag
packetdiag {
  colwidth = 28;
  node_height = 72;
  internet [label = "Client"];
  gateway [label = "Kroki"];
  docx [label = "DOCX"];
  internet -> gateway -> docx;
}
```

## Seqdiag

Source:

```text
seqdiag {
  Developer -> Renderer [label = "render doc"];
  Renderer -> Kroki [label = "convert diagram"];
  Kroki => Renderer [label = "PNG"];
  Renderer => Developer [label = "DOCX"];
}
```

Rendered:

```seqdiag
seqdiag {
  Developer -> Renderer [label = "render doc"];
  Renderer -> Kroki [label = "convert diagram"];
  Kroki => Renderer [label = "PNG"];
  Renderer => Developer [label = "DOCX"];
}
```

## Blockdiag

Source:

```text
blockdiag {
  orientation = portrait;
  Author [label = "Author"];
  Renderer [label = "Renderer"];
  Docx [label = "DOCX"];
  Author -> Renderer -> Docx;
}
```

Rendered:

```blockdiag
blockdiag {
  orientation = portrait;
  Author [label = "Author"];
  Renderer [label = "Renderer"];
  Docx [label = "DOCX"];
  Author -> Renderer -> Docx;
}
```

## Review Notes

- Confirm each rendered diagram stays within a reasonable page footprint.
- Confirm the code snippets remain visible as text in the DOCX.
- Confirm the output works for Mermaid plus five additional diagram languages.
