# Ansible Dev Spaces Demo

This repository provides a ready-to-run OpenShift Dev Spaces (Che) workspace for iterating on Ansible automation. It pulls in the upstream `ansible-dev-tools` workspace helpers, installs a curated set of Galaxy roles and collections, and exposes opinionated playbooks you can use as a smoke test for the environment.

The implementation borrows ideas from the original [`redhat-developer-demos/ansible-devspaces-demo`](https://github.com/redhat-developer-demos/ansible-devspaces-demo) while updating the layout to match the current DevWorkspace and Devfile 2.x specifications.

## What's Included

- **DevWorkspace definition** (`devspace.yaml`) and **Devfile 2.2** (`devfile.yaml`) describing the workspace container, commands, and startup hooks.
- **Bootstrap automation** (`scripts/clone-repos.sh` + `repos-to-clone.txt`) that materialises upstream Ansible dependencies inside `.workspace/` on every launch.
- **Project configuration** (`ansible.cfg`, `group_vars/`, `inventories/`) tuned for local execution against the Dev Spaces container.
- **Sample playbook** (`playbooks/site.yml`) that demonstrates how to reference injected OpenShift secrets and produce a reusable credentials file for downstream automation.
- **Galaxy dependencies** (`requirements.yml`) pinning widely used community roles and collections so linting, Molecule, and playbook runs behave consistently.
- **Makefile helpers** (`Makefile`) wrapping the most common bootstrap and verification workflows (`make bootstrap`, `make lint`, `make test`, `make smoke`).

## Launching in Dev Spaces

1. **Create required secrets** – provision an OpenShift secret named `domain-credentials` in the same namespace as your DevWorkspace. It must contain `username` and `password` keys so the workspace can export `DOMAIN_USERNAME` and `DOMAIN_PASSWORD` environment variables.
2. **Start the workspace** – point Dev Spaces at this repository. The DevWorkspace controller consumes `devspace.yaml`, spins up the `quay.io/ansible/toolset:latest` image, and applies the secret-backed environment variables automatically.
3. **Automatic bootstrap** – the `postStart` events in both the DevWorkspace and Devfile run `./scripts/clone-repos.sh` and `ansible-galaxy install -r requirements.yml` so upstream content and dependencies are ready immediately.
4. **Run the smoke test** – execute the `Run sample site playbook` command (or run `ansible-playbook playbooks/site.yml` manually). The playbook installs developer tooling, surfaces the injected domain credentials, and writes `.workspace/domain_credentials.yml` for reuse.
5. **Iterate with fast feedback** – leverage the built-in commands (e.g. `Run Ansible lint checks`, `Run test suite`) or call the Makefile targets directly (`make lint`, `make test`, `make smoke`) to validate changes as you work.

If you prefer to launch the workspace locally, run the same bootstrap steps from a terminal:

```bash
git clone https://github.com/KhalilGibrotha/ansible-devspaces
cd ansible-devspaces
git checkout main
make bootstrap
make test
make smoke
```

## Working with Secrets Inside Playbooks

Secrets passed through OpenShift (or Che) appear as environment variables on the workspace container. The repository ships with `group_vars/all/secrets.yml` that resolves the `DOMAIN_USERNAME` and `DOMAIN_PASSWORD` variables and makes them available to every playbook. You can reference them directly:

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

By default the sample playbook copies those values to `.workspace/domain_credentials.yml`. Update or remove that task if you want to manage secrets differently.

## Repository Structure

```
Makefile
ansible.cfg
devfile.yaml
devspace.yaml
group_vars/
└── all/
    └── secrets.yml
inventories/
└── hosts.ini
playbooks/
└── site.yml
requirements.yml
repos-to-clone.txt
scripts/
└── clone-repos.sh
```

## Next Steps

- Add Molecule scenarios and CI workflows tailored to the roles you build in this workspace.
- Extend `repos-to-clone.txt` with the application repositories you plan to test against.
- Replace the sample playbook with your project-specific automation once the workspace bootstrap flow meets your needs.

Contributions and feedback are welcome!
