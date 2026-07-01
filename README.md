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
  that materializes upstream Ansible dependencies inside `.workspace/` on every
  launch.
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
3. **Automatic bootstrap**: the `postStart` events in both the DevWorkspace and
   Devfile run `./scripts/devspace-post-start.sh`, which attempts
   `./scripts/clone-repos.sh` and `ansible-galaxy install -r requirements.yml`
   on a best-effort basis so the IDE can still open if an external dependency
   is temporarily unavailable.
4. **Run the smoke test**: execute the `Run sample site playbook` command or
   run `ansible-playbook playbooks/site.yml` manually. The playbook installs
   developer tooling, surfaces the injected domain credentials, and writes
   `.workspace/domain_credentials.yml` for reuse.
5. **Iterate with fast feedback**: leverage the built-in commands or call the
   Makefile targets directly (`make lint`, `make test`, `make smoke`) to
   validate changes as you work.

If bootstrap steps fail during workspace startup, open a terminal after the IDE
loads and rerun them manually:

```bash
./scripts/clone-repos.sh
ansible-galaxy install -r requirements.yml --force
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
  docx-renderer.env.example
  docx-renderer.sh
tests/
  test_docx_renderer.py
```

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
cover branding through to `docx-build`.

Typical usage:

```bash
make docx-renderer-test
cp scripts/docx-renderer.env.example .docx-renderer.env
# update .docx-renderer.env for your namespace, PVC, and document paths
set -a && . ./.docx-renderer.env && set +a
./scripts/docx-renderer.sh apply-kroki
./scripts/docx-renderer.sh run-job
./scripts/docx-renderer.sh wait-job
./scripts/docx-renderer.sh logs-job
```

There is a ready-made test document at
`examples/docx/sample-mermaid-architecture.md` plus a matching sample
`examples/docx/org.yaml` file for cover-page metadata.

## Next Steps

- Add Molecule scenarios and CI workflows tailored to the roles you build in
  this workspace.
- Extend `repos-to-clone.txt` with the application repositories you plan to
  test against.
- Replace the sample playbook with your project-specific automation once the
  workspace bootstrap flow meets your needs.

Contributions and feedback are welcome.
