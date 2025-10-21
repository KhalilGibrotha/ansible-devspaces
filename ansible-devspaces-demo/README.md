# Ansible Devspaces Demo

This repository captures the Dev Spaces definition we ship to our Ansible engineering teams. It assembles upstream building blocks, bootstraps the container workspace, and brings in project-specific playbooks, inventories, and tooling.

We started from the excellent [`redhat-developer-demos/ansible-devspaces-demo`](https://github.com/redhat-developer-demos/ansible-devspaces-demo) and layered in our own automation. Many thanks to the original authors for the foundation.

## Layered Architecture

- **Upstream tooling** (`ansible-dev-tools`): Provides the execution environment, Molecule configuration, linting profiles, and VS Code extension recommendations. We selectively sparse-checkout the `devspaces` subtree while also cloning the full repository for Molecule test assets.
- **Dev Spaces definition** (`devfile.yaml` and `devspace.yaml`): Declares the runtime image, commands, resource limits, and deployment hooks used by Red Hat OpenShift Dev Spaces.
- **Workspace bootstrap** (`scripts/clone-repos.sh` + `repos-to-clone.txt`): Fetches upstream dependencies and adjacent projects during environment startup so every workspace opens with the same folder layout.
- **Automation content** (`playbooks/`, `roles/`, `inventories/`, `requirements.yml`): Houses the playbooks and roles teams iterate on inside the environment.
- **Editor experience** (`workspace.code-workspace`, `.vscode/`, `.devcontainer/`): Aligns VS Code settings, extensions, and container defaults with what the upstream tools expect.

## Upstream Requirements

- Red Hat OpenShift Dev Spaces 3.x (or Che 7+) to consume the `devfile.yaml`
- Internet access from the workspace container to clone GitHub repositories listed in `repos-to-clone.txt`
- Cluster permissions to apply or update resources under the `devspaces` namespace when running `devspace.yaml`
- `oc` CLI available within the workspace image if you plan to apply the Dev Space orchestration from a terminal
- Git credentials configured in Dev Spaces so private forks of the upstream repositories can be fetched when required

## Dev Space Provisioning Flow

1. **Workspace launch**: Dev Spaces reads `devfile.yaml`, pulls the specified container image, and seeds environment variables.
2. **Pre-deploy hook**: `./scripts/clone-repos.sh` runs automatically (see `devspace.yaml`), cloning every entry in `repos-to-clone.txt`. URLs ending in `/tree/<branch>/<path>` trigger a sparse checkout of just that subtree while still fetching the full repo when requested.
3. **Dependency install**: The `Install dependencies` command installs Ansible collections and roles from `requirements.yml` inside the workspace container.
4. **Development workflow**: Engineers open VS Code (either the web IDE or a connected desktop) using `workspace.code-workspace`, gaining linting, Molecule, and extension defaults from `ansible-dev-tools`.
5. **Execution**: Use the provided commands (e.g., `Run playbook`) or your own `ansible-playbook` / `molecule` invocations.

## Repository Map

- `devfile.yaml`: Dev Spaces component/image definition.
- `devspace.yaml`: Namespaced deployment configuration plus pre/post hooks.
- `repos-to-clone.txt`: One URL per line, optional destination folder in column two. Maintained so new teams inherit identical checkouts.
- `scripts/clone-repos.sh`: Idempotent clone script that understands sparse checkouts and skips folders that already exist.
- `playbooks/`, `roles/`, `inventories/`: Primary Ansible content.
- `requirements.yml`: Galaxy dependencies the workspace installs on boot.
- `.devcontainer/`, `.vscode/`, `workspace.code-workspace`: Developer experience settings.

## Local Testing Outside Dev Spaces

You can exercise the same workflow locally:

```bash
git clone https://github.com/KhalilGibrotha/ansible-devspaces
cd ansible-devspaces/ansible-devspaces-demo
./scripts/clone-repos.sh
ansible-galaxy install -r requirements.yml
code workspace.code-workspace
```

Run Molecule scenarios or playbooks exactly as they would execute inside Dev Spaces to ensure changes behave consistently.

## Contributing

Please submit issues or pull requests if upstream requirements change or new layers must be integrated. Remember to credit `redhat-developer-demos/ansible-devspaces-demo` when sharing derivative work, just as we do here.