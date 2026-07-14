# Ansible Dev Spaces Demo

This repository provides a ready-to-run OpenShift Dev Spaces (Che) workspace
for iterating on Ansible automation. It pulls in the upstream
`ansible-dev-tools` workspace helpers, installs a curated set of Galaxy roles
and collections, and exposes opinionated playbooks you can use as a smoke test
for the environment.

The implementation borrows ideas from the original
[`redhat-developer-demos/ansible-devspaces-demo`](https://github.com/redhat-developer-demos/ansible-devspaces-demo)
while updating the layout to match the current DevWorkspace and Devfile 2.x
specifications.

## What's Included

- **DevWorkspace definition** (`devspace.yaml`) and **Devfile 2.2**
  (`devfile.yaml`) describing the workspace container, commands, and startup
  hooks.
- **Bootstrap automation** (`scripts/clone-repos.sh` + `repos-to-clone.txt`)
  that materializes upstream Ansible dependencies into the sibling
  `/projects/workspace-repos/` folder on every launch.
- **Public architecture documentation starter**
  (`/projects/workspace-repos/architecture-docs-starter`) so authors have a reusable
  content-repo seed with baseline templates, manifests, and lint/editor
  settings alongside the tooling repo.
- **Bootstrap wrapper** (`scripts/devspace-bootstrap.sh`) that runs clone and
  Galaxy dependency install as one explicit post-start action.
- **Project configuration** (`ansible.cfg`, `group_vars/`, `inventories/`)
  tuned for local execution against the Dev Spaces container.
- **Sample playbook** (`playbooks/site.yml`) that demonstrates how to reference
  injected OpenShift secrets and produce a reusable credentials file for
  downstream automation.
- **Galaxy dependencies** (`requirements.yml`) pinning widely used community
  roles and collections so linting, Molecule, and playbook runs behave
  consistently.
- **Makefile helpers** (`Makefile`) wrapping the most common bootstrap and
  verification workflows (`make bootstrap`, `make lint`, `make test`,
  `make smoke`).
- **Experimental DOCX rendering path**
  (`experiments/docx_renderer/`, `scripts/docx-renderer.sh`,
  `k8s/docx-renderer/`) for Mermaid-aware Markdown-to-DOCX rendering in
  isolated pods.
- **Kroki sidecar smoke test** (`scripts/verify-kroki.py`) for validating that
  a local Kroki sidecar is reachable from the main Dev Spaces container.
- **Diagram lint step** (`scripts/lint_diagrams.py`) for validating Markdown
  diagram fences through Kroki before attempting a full DOCX render.
- **Static preflight step** (`scripts/preflight_docx.py`) for catching
  front-matter and source-text issues before diagram or DOCX processing.
- **Local DOCX render wrapper** (`scripts/docx-render-local.sh`) for generating
  DOCX output inside the workspace using the Kroki sidecar and a local Python
  virtual environment.
- **Manifest runner** (`scripts/docx_manifest.py`) for listing, linting, and
  rendering multiple manifest-managed DOCX documents.
- **Workflow reference** ([docs/docx-workflow.md](docs/docx-workflow.md))
  documenting the current single-document flow and the proposed
  manifest-driven multi-document model.

## Launching in Dev Spaces

1. **Create required secrets**: provision an OpenShift secret named
   `domain-credentials` in the same namespace as your DevWorkspace. It must
   contain `username` and `password` keys so the workspace can export
   `DOMAIN_USERNAME` and `DOMAIN_PASSWORD` environment variables.
2. **Start the workspace**: point Dev Spaces at this repository. The
   DevWorkspace controller consumes `devspace.yaml`, spins up the
   `ghcr.io/ansible/ansible-devspaces` workspace image used by the upstream
   Red Hat demo, and applies the secret-backed environment variables
   automatically.
3. **Manual bootstrap after workspace start**: once the IDE opens, run the
   `Bootstrap workspace dependencies` command from the Dev Spaces UI, or run
   `bash ./scripts/devspace-bootstrap.sh` from the terminal to fetch upstream
   content and dependencies. Cloned repos will appear in the visible
   sibling `/projects/workspace-repos/` folder.
   The default clone list includes both `dac-toolkit` and the public
   `architecture-docs-starter` repo for documentation-focused work.
4. **Run the smoke test**: execute the `Run sample site playbook` command or
   run `ansible-playbook playbooks/site.yml` manually. The playbook installs
   developer tooling, surfaces the injected domain credentials, and writes
   `.workspace/domain_credentials.yml` for reuse.
5. **Iterate with fast feedback**: leverage the built-in commands or call the
   Makefile targets directly (`make lint`, `make test`, `make smoke`) to
   validate changes as you work.
6. **Verify Kroki sidecar**: run the `Verify Kroki sidecar` command from the
   Dev Spaces UI or `make kroki-sidecar-test` from the terminal to confirm the
   sidecar responds to `/health` and can render a sample Mermaid diagram.
7. **Validate document diagrams before rendering**: run the `Validate Markdown
   diagrams` command from the Dev Spaces UI or `make diagram-lint` from the
   terminal to catch unsupported or invalid diagram blocks early.
8. **Run static preflight checks**: run `make docx-preflight` for a single
   document or `make docx-preflight-all` for the manifest-managed document set.
9. **Validate manifest-managed documents**: run the `Validate manifest-managed
   docs` command from the Dev Spaces UI or `make diagram-lint-all` from the
   terminal to lint every document listed in the default manifest.
10. **Render sample DOCX locally**: run the `Render sample DOCX locally` command
   from the Dev Spaces UI or `make docx-render-local` from the terminal.
11. **Render manifest-managed documents**: run the `Render manifest-managed DOCX
    docs` command from the Dev Spaces UI or `make docx-render-all` from the
    terminal.

After the workspace opens, run bootstrap manually:

```bash
bash ./scripts/devspace-bootstrap.sh
```

If you prefer to launch the workspace locally, run the same bootstrap steps
from a terminal:

```bash
git clone https://github.com/KhalilGibrotha/ansible-devspaces
cd ansible-devspaces
git checkout develop
make bootstrap
make test
make smoke
```

## Working with Secrets Inside Playbooks

Secrets passed through OpenShift or Che appear as environment variables on the
workspace container. The repository ships with `group_vars/all/secrets.yml`
that resolves the `DOMAIN_USERNAME` and `DOMAIN_PASSWORD` variables and makes
them available to every playbook. You can reference them directly:

```yaml
- name: Use injected credentials
  ansible.builtin.uri:
    url: https://internal.example.com/auth
    method: POST
    body_format: json
    body:
      username: "{{ domain_username }}"
      password: "{{ domain_password }}"
```

By default the sample playbook copies those values to
`.workspace/domain_credentials.yml`. Update or remove that task if you want to
manage secrets differently.

## Repository Structure

```text
Makefile
ansible.cfg
devfile.yaml
devspace.yaml
experiments/
  docx_renderer/
    render_with_kroki.py
group_vars/
  all/
    secrets.yml
inventories/
  hosts.ini
k8s/
  docx-renderer/
    kroki.yaml
    README.md
playbooks/
  site.yml
requirements.yml
repos-to-clone.txt
scripts/
  clone-repos.sh
  devspace-bootstrap.sh
  docx-render-local.env.example
  docx-render-local.sh
  docx-renderer.env.example
  docx-renderer.sh
tests/
  test_docx_renderer.py
```

## Kroki Sidecar

The Devfile now includes a `kroki-sidecar` gateway container plus a
`kroki-mermaid-sidecar` companion container in the same workspace pod. This
matches the official Kroki model where Mermaid is delegated to a separate
companion service. From the main `ansible-tools` container perspective, Kroki
is exposed on `http://127.0.0.1:8000`.

To verify the sidecar after the workspace starts:

```bash
make kroki-sidecar-test
```

Or run the `Verify Kroki sidecar` command in the Dev Spaces UI. Successful
output confirms both the health endpoint and a sample Mermaid SVG render work.

## Diagram Authoring Workflow

For documentation work, validate diagram fences before committing or building a
DOCX:

```bash
make docx-preflight
make diagram-lint
```

This scans Markdown under `examples/docx/`, finds Kroki-supported fenced code
blocks, and submits each one to the local Kroki sidecar. Failures are reported
with file, line number, and diagram language so authors can fix the source
before running `docx-build`.

The aggregate `make test` target now includes `make diagram-lint`, so broken
diagram source is treated as a test failure in the workspace.

`make docx-render-local` also runs this validation step automatically against
the selected input Markdown before it rewrites diagram fences or builds the
final DOCX.

If dense diagrams still look soft in the generated DOCX, raise the shared
diagram render scale before running lint or render commands:

```bash
export DOCX_BUILDER_DIAGRAM_RENDER_SCALE=3
```

The default is `2`. This scale is applied to all Kroki-backed diagram types,
not only Mermaid, so PlantUML, Graphviz, D2, Packetdiag, and similar diagram
blocks are rendered at a higher pixel density before `docx-build` embeds them.

For multi-document workflows, the repository now includes a manifest runner.
The default manifest path is `examples/docx/render-manifest.example.yaml`.

Manifest-oriented commands:

```bash
make docx-preflight-all
make diagram-lint-all
make docx-render-all
make docx-render-one DOC_ID=sample-gallery
```

These commands route through `scripts/docx_manifest.py`, which reads the
manifest, selects the requested documents, and reuses the existing local DOCX
render path per document.

The workspace also recommends a small set of VS Code extensions for previewing
diagram-heavy Markdown:

- `shd101wyy.markdown-preview-enhanced`
- `bierner.markdown-mermaid`
- `jebbs.plantuml`
- `tintinweb.graphviz-interactive-preview`

The best all-around preview path for this repo is `Markdown Preview Enhanced`,
because it handles Markdown-centric authoring with embedded Mermaid, PlantUML,
and Graphviz blocks in one UI.

## Local Mermaid-to-DOCX Flow

The primary Mermaid render path is now workspace-local rather than Kubernetes
Job-based. After running bootstrap, the local wrapper will:

1. create or reuse a Python virtual environment
2. clone `dac-toolkit` into `/projects/workspace-repos/` automatically if it is missing
3. install `docx-builder` from `/projects/workspace-repos/dac-toolkit/docx_builder`
4. rewrite Mermaid fences to PNG assets through the Kroki sidecar
5. run `docx-build` to generate the DOCX

Quick start:

```bash
cp scripts/docx-render-local.env.example .docx-render-local.env
set -a && . ./.docx-render-local.env && set +a
make docx-render-local
```

The default sample input is `examples/docx/sample-diagram-gallery.md` and the
default output path is `examples/docx/output/sample-diagram-gallery.docx`.

The sample gallery currently exercises Mermaid plus five additional
Kroki-supported languages:

- `plantuml`
- `graphviz`
- `c4plantuml`
- `seqdiag`
- `blockdiag`

A manifest-oriented next-step design is documented in
`docs/docx-workflow.md`. The current default manifest is
`docs/render-manifest.yaml`, and a sample reference manifest remains at
`examples/docx/render-manifest.example.yaml`.

## Experimental Mermaid-to-DOCX Rendering

This repo now includes an isolated rendering path for Markdown documents that
need Mermaid diagrams embedded in DOCX output without modifying the base Dev
Space image.

The experiment works like this:

1. `repos-to-clone.txt` clones `dac-toolkit` into the workspace alongside this
   repo.
2. `k8s/docx-renderer/kroki.yaml` deploys a namespace-local Kroki service.
3. `experiments/docx_renderer/render_with_kroki.py` rewrites Mermaid fences to
   PNG image references by calling Kroki.
4. `scripts/docx-renderer.sh` launches a short-lived Kubernetes Job that mounts
   the shared workspace PVC, installs `docx-builder` from the cloned
   `dac-toolkit`, and runs `docx-build` against the rewritten Markdown.

`scripts/docx-renderer.env.example` also exposes optional `ORG_YAML` and
`LOGO_PATH` variables so the render job can feed organization metadata and
cover branding through to `docx-build`. It also exposes
`DOCX_BUILDER_DIAGRAM_RENDER_SCALE` for increasing diagram sharpness across all
Kroki-supported diagram types.

Typical usage:

```bash
make docx-renderer-test
cp scripts/docx-renderer.env.example .docx-renderer.env
# update .docx-renderer.env for your namespace, PVC, and document paths
set -a && . ./.docx-renderer.env && set +a
bash ./scripts/docx-renderer.sh apply-kroki
bash ./scripts/docx-renderer.sh run-job
bash ./scripts/docx-renderer.sh wait-job
bash ./scripts/docx-renderer.sh logs-job
```

There is a ready-made test document at
`examples/docx/sample-diagram-gallery.md` plus a matching sample
`examples/docx/org.yaml` file for cover-page metadata.

## Next Steps

- Add Molecule scenarios and CI workflows tailored to the roles you build in
  this workspace.
- Extend `repos-to-clone.txt` with the application repositories you plan to
  test against.
- Replace the sample playbook with your project-specific automation once the
  workspace bootstrap flow meets your needs.

Contributions and feedback are welcome.
